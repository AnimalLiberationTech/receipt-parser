from datetime import datetime, date, timezone
from enum import StrEnum, IntEnum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import Field, EmailStr

from src.schemas.schema_base import SchemaBase


class UserRightsGroup(StrEnum):
    NORMAL = "normal"
    TESTER = "tester"
    CONTENT_MODERATOR = "content_moderator"
    GLOBAL_MODERATOR = "everything_moderator"
    ADMINISTRATOR = "administrator"


class UserRightsGroupCode(IntEnum):
    NORMAL = 1
    TESTER = 2
    CONTENT_MODERATOR = 3
    GLOBAL_MODERATOR = 4
    ADMINISTRATOR = 5


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    TRANSGENDER = "transgender"
    NON_BINARY = "non-binary"


class GenderCode(IntEnum):
    MALE = 1
    FEMALE = 2
    TRANSGENDER = 3
    NON_BINARY = 4


class User(SchemaBase):
    id: Optional[UUID] = Field(default_factory=uuid4)
    email: EmailStr
    name: str
    login_generation: int = 1
    banned: bool = False
    self_description: str | None = None
    gender: Gender | None = None
    birthday: date | None = None
    user_rights_group: UserRightsGroup = UserRightsGroup.NORMAL
    avatar_id: UUID | None = None
    created_at: datetime = datetime.now(tz=timezone.utc)
