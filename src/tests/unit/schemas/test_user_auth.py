from unittest import TestCase

from src.schemas.user_auth import UserAuth, GoogleUserAuth
from pydantic_core._pydantic_core import ValidationError  # noqa


class TestUserAuth(TestCase):
    def test_wrong_types(self):
        with self.assertRaises(ValidationError) as ctx:
            UserAuth(email="not_email", name="Test User")
        errors = ctx.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["loc"], ("email",))
        self.assertTrue(errors[0]["msg"].startswith("value is not a valid email address"))


class TestGoogleUserAuth(TestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.name = "Test User"
        self.google_id = "123456789"
        self.avatar_url = "http://example.com/avatar.jpg"
        self.locale = "en"

    def test_from_token(self):
        data = {
            "email": self.email,
            "name": self.name,
            "given_name": "",
            "sub": self.google_id,
            "picture": self.avatar_url,
            "locale": self.locale,
        }
        google_user_auth = GoogleUserAuth.from_token(data)
        self.assertEqual(google_user_auth.email, self.email)
        self.assertEqual(google_user_auth.name, self.name)
        self.assertEqual(google_user_auth.google_id, self.google_id)
        self.assertEqual(google_user_auth.avatar_url, self.avatar_url)
        self.assertEqual(google_user_auth.locale, self.locale)
