from datetime import datetime, date
from unittest import TestCase
from uuid import UUID

from pydantic import ValidationError

from src.schemas.user import User, UserRightsGroup, Gender


class TestUser(TestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.name = "Test User"
        self.login_generation = 1
        self.banned = False
        self.self_description = "This is a test user"
        self.gender = Gender.MALE
        self.birthday = date.today()
        self.user_rights_group = UserRightsGroup.NORMAL
        self.avatar_id = UUID("12345678123456781234567812345678")

    def test_auto_generated_fields(self):
        user = User(
            email=self.email,
            name=self.name,
            login_generation=self.login_generation,
            banned=self.banned,
            self_description=self.self_description,
            gender=self.gender,
            birthday=self.birthday,
            user_rights_group=self.user_rights_group,
            avatar_id=self.avatar_id,
        )
        self.assertIsInstance(user, User)
        self.assertIsInstance(user.id, UUID)
        self.assertIsInstance(user.created_at, datetime)

    def test_wrong_types(self):
        with self.assertRaises(ValidationError) as ctx:
            User(
                email="invalid_email",
                name=self.name,
                login_generation=self.login_generation,
                banned=self.banned,
                self_description=self.self_description,
                gender=self.gender,
                birthday=self.birthday,
                user_rights_group=self.user_rights_group,
                avatar_id=self.avatar_id,
            )
        errors = ctx.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["loc"], ("email",))
        self.assertTrue(errors[0]["msg"].startswith("value is not a valid email address"))

    def test_wrong_enum_values(self):
        with self.assertRaises(ValidationError) as ctx:
            User(
                email=self.email,
                name=self.name,
                login_generation=self.login_generation,
                banned=self.banned,
                self_description=self.self_description,
                gender="invalid_gender",
                birthday=self.birthday,
                user_rights_group="invalid_rights_group",
                avatar_id=self.avatar_id,
            )
        errors = ctx.exception.errors()
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]["loc"], ("gender",))
        self.assertTrue(errors[0]["msg"][:23] == f"Input should be '{Gender.MALE}',")
        self.assertEqual(errors[1]["loc"], ("user_rights_group",))
        self.assertEqual(
            errors[1]["msg"][:25], f"Input should be '{UserRightsGroup.NORMAL}',"
        )
