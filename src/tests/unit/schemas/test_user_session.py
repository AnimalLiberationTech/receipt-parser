from datetime import datetime
from unittest import TestCase
from uuid import UUID

from src.schemas.user_identity import IdentityProvider
from src.schemas.user_session import UserSessionCookie, UserSession, GoogleUserSession
from src.tests import USER_ID_1, STATE_ID


class TestUserSessionCookie(TestCase):
    def setUp(self):
        self.session_id = UUID(USER_ID_1)
        self.identity_provider = IdentityProvider.GOOGLE
        self.user_id = UUID(USER_ID_1)

    def test_fields_assignment(self):
        user_session_cookie = UserSessionCookie(
            session_id=self.session_id,
            identity_provider=self.identity_provider,
            user_id=self.user_id,
        )
        self.assertEqual(user_session_cookie.session_id, self.session_id)
        self.assertEqual(user_session_cookie.identity_provider, self.identity_provider)
        self.assertEqual(user_session_cookie.user_id, self.user_id)


class TestUserSession(TestCase):
    def setUp(self):
        self.identity_provider = IdentityProvider.GOOGLE
        self.user_id = UUID(USER_ID_1)
        self.user_name = "Test User"

    def test_fields_assignment(self):
        user_session = UserSession(
            identity_provider=self.identity_provider,
            user_id=self.user_id,
            user_name=self.user_name,
        )
        self.assertIsInstance(user_session.id, UUID)
        self.assertEqual(user_session.identity_provider, self.identity_provider)
        self.assertEqual(user_session.user_id, self.user_id)
        self.assertEqual(user_session.user_name, self.user_name)

    def test_auto_generated_fields(self):
        user_session = UserSession(
            identity_provider=self.identity_provider,
            user_id=self.user_id,
            user_name=self.user_name,
        )
        self.assertIsInstance(user_session.created_at, datetime)


class TestGoogleUserSession(TestCase):
    def setUp(self):
        self.user_id = UUID(USER_ID_1)
        self.user_name = "Test User"

    def test_fields_assignment(self):
        google_user_session = GoogleUserSession(
            user_id=self.user_id, user_name=self.user_name, state=STATE_ID
        )
        self.assertIsInstance(google_user_session.id, UUID)
        self.assertEqual(google_user_session.identity_provider, IdentityProvider.GOOGLE)
        self.assertEqual(google_user_session.user_id, self.user_id)
        self.assertEqual(google_user_session.user_name, self.user_name)
        self.assertEqual(google_user_session.state, STATE_ID)

    def test_auto_generated_fields(self):
        google_user_session = GoogleUserSession(
            user_id=self.user_id, user_name=self.user_name, state=STATE_ID
        )
        self.assertIsInstance(google_user_session.created_at, datetime)

    def test_missing_state(self):
        with self.assertRaises(ValueError):
            GoogleUserSession(user_id=self.user_id, user_name=self.user_name, state=None)
