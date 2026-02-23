import pytest

pytest.skip("disabled", allow_module_level=True)

from time import time
from unittest import TestCase
from unittest.mock import patch, MagicMock
from uuid import UUID

from src.adapters.auth.google_auth import GoogleAuth
from src.schemas.user_auth import GoogleUserAuth
from src.schemas.user_identity import IdentityProvider
from src.schemas.user_session import GoogleUserSession
from src.tests import STATE_ID, SESSION_ID, USER_ID_1


class TestGoogleAuth(TestCase):
    @patch("src.adapters.auth.google_auth.init_db_session")
    @patch("src.adapters.auth.google_auth.Flow.from_client_secrets_file")
    def setUp(self, mock_flow_from_file, mock_db_session):
        self.logger = MagicMock()
        self.google_auth = GoogleAuth(self.logger)
        self.mock_flow = mock_flow_from_file
        self.mock_db_session = mock_db_session

    def test_init(self):
        self.assertIsNotNone(self.google_auth)
        self.mock_flow.assert_called_once()
        self.mock_db_session.assert_called_once_with(self.logger)

    @patch("src.adapters.auth.google_auth.id_token.verify_oauth2_token")
    @patch("src.adapters.auth.google_auth.Request")
    @patch("src.adapters.auth.google_auth.Session")
    @patch("src.adapters.auth.google_auth.CacheControl")
    def test_verify_token(
        self, mock_cache_control, mock_session, mock_request, mock_verify_token
    ):
        self.google_auth.get_google_client_id = MagicMock(return_value="google_client_id")
        mock_verify_token.return_value = {
            "exp": time() + 1000,
            "name": "John Doe",
            "email": "j@doe.eu",
            "sub": "1234567890",
        }

        self.google_auth.verify_token("http://test.com")

        mock_cache_control.assert_called_once_with(mock_session.return_value)
        mock_request.assert_called_once_with(session=mock_cache_control.return_value)
        mock_verify_token.assert_called_once()

    def test_create_session(self):
        auth_url = "http://auth_url.com"
        self.google_auth.flow.authorization_url.return_value = (auth_url, STATE_ID)
        self.mock_db_session.return_value.create_one.return_value = SESSION_ID

        auth_url, cookie = self.google_auth.create_session()

        self.assertEqual(auth_url, auth_url)
        self.assertEqual(cookie.session_id, UUID(SESSION_ID))
        self.assertEqual(cookie.identity_provider, IdentityProvider.GOOGLE)
        self.google_auth.flow.authorization_url.assert_called_once()
        self.mock_db_session.return_value.create_one.assert_called_once()

    def test_get_new_session(self):
        self.mock_db_session.return_value.read_one.return_value = {
            "state": STATE_ID,
            "_id": SESSION_ID,
        }
        result = self.google_auth.get_new_session(UUID(SESSION_ID))
        self.assertEqual(result.id, UUID(SESSION_ID))
        self.assertEqual(result.state, STATE_ID)
        self.mock_db_session.return_value.read_one.assert_called_once_with(
            SESSION_ID, partition_key=IdentityProvider.GOOGLE
        )

    def test_update_session(self):
        self.mock_db_session.return_value.read_one.return_value = {
            "user_id": USER_ID_1,
            "_id": "google_id",
            "provider": IdentityProvider.GOOGLE,
        }
        session = GoogleUserSession(id=UUID(SESSION_ID), state=STATE_ID)
        google_auth = GoogleUserAuth(
            email="j@doe.eu",
            name="John Doe",
            google_id="google_id",
            avatar_url=None,
            locale=None,
        )

        result = self.google_auth.update_session(session, google_auth)

        self.assertEqual(result.user_id, UUID(USER_ID_1))
        self.assertEqual(result.user_name, google_auth.name)
        self.mock_db_session.return_value.read_one.assert_called_once_with(
            google_auth.google_id, partition_key=IdentityProvider.GOOGLE
        )
        self.mock_db_session.return_value.update_one.assert_called_once_with(
            SESSION_ID, result.model_dump(mode="json")
        )
