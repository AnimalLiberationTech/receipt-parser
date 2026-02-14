from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import MagicMock, patch
from uuid import UUID

from src.helpers.session import validate_session, SESSION_VALIDITY_DAYS
from src.schemas.user_identity import IdentityProvider
from src.schemas.user_session import UserSession, UserSessionCookie
from src.tests import SESSION_ID, USER_ID_1


class TestSession(TestCase):
    @patch("src.helpers.session.datetime")
    def setUp(self, mock_datetime):
        self.logger = MagicMock()
        self.now = datetime.now()
        mock_datetime.now.return_value = self.now

    def test_validate_session_missing_cookie(self):
        self.assertIsNone(validate_session(None, self.logger))

    @patch("src.helpers.session.init_db_session")
    def test_validate_missing_session(self, mock_db_session):
        mock_db_session.return_value.read_one.return_value = None
        cookie = UserSessionCookie(
            session_id=UUID(SESSION_ID), identity_provider=IdentityProvider.GOOGLE
        )

        self.assertIsNone(validate_session(cookie, self.logger))

    @patch("src.helpers.session.init_db_session")
    def test_validate_expired_session(self, mock_db_session):
        mock_db_session.return_value.read_one.return_value = {
            "_id": "1",
            "user_id": "test",
            "created_at": (
                self.now - timedelta(days=SESSION_VALIDITY_DAYS + 1)
            ).isoformat(),
        }
        cookie = UserSessionCookie(
            session_id=UUID(SESSION_ID), identity_provider=IdentityProvider.GOOGLE
        )

        self.assertIsNone(validate_session(cookie, self.logger))

    @patch("src.helpers.session.init_db_session")
    def test_validate_session(self, mock_db_session):
        mock_db_session.return_value.read_one.return_value = {
            "_id": SESSION_ID,
            "user_id": USER_ID_1,
            "user_name": "John Doe",
            "identity_provider": "google",
            "created_at": (
                self.now - timedelta(days=SESSION_VALIDITY_DAYS - 1)
            ).isoformat(),
        }
        cookie = UserSessionCookie(
            session_id=UUID(SESSION_ID), identity_provider=IdentityProvider.GOOGLE
        )

        result = validate_session(cookie, self.logger)

        self.assertEqual(result.id, UUID(SESSION_ID))
        self.assertEqual(result.identity_provider, IdentityProvider.GOOGLE)
        self.assertEqual(result.user_id, UUID(USER_ID_1))
        self.assertIsInstance(result.created_at, datetime)
