from typing import Self

from pydantic import EmailStr

from src.schemas.schema_base import SchemaBase


class UserAuth(SchemaBase):
    email: EmailStr
    name: str


class GoogleUserAuth(UserAuth):
    google_id: str
    avatar_url: str | None
    locale: str | None

    @classmethod
    def from_token(cls, data: dict) -> Self:
        return cls(
            email=data.get("email"),
            name=" ".join([data[key] for key in ["name", "given_name"] if data.get(key)]),
            google_id=data.get("sub"),
            avatar_url=data.get("picture"),
            locale=data.get("locale"),
        )
