from datetime import datetime
from unittest import TestCase
from uuid import UUID

from pydantic_core._pydantic_core import ValidationError  # noqa

from src.schemas.user_identity import UserIdentity, IdentityProvider
from src.tests import USER_ID_1


class TestUserIdentity(TestCase):
    def setUp(self):
        self.provider = IdentityProvider.GOOGLE
        self.user_id = UUID(USER_ID_1)

    def test_auto_generated_fields(self):
        user_identity = UserIdentity(
            id="123456789", provider=self.provider, user_id=self.user_id
        )
        self.assertIsInstance(user_identity.created_at, datetime)

    def test_wrong_types(self):
        with self.assertRaises(ValidationError) as ctx:
            UserIdentity(id="123456789", provider="provider", user_id="user_id")

        errors = ctx.exception.errors()
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]["loc"], ("provider",))
        self.assertEqual(errors[0]["msg"], "Input should be 'google'")
        self.assertEqual(errors[1]["loc"], ("user_id",))
        self.assertTrue(errors[1]["msg"].startswith("Input should be a valid UUID"))
