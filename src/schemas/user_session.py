from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.schemas.schema_base import SchemaBase
from src.schemas.user_identity import IdentityProvider


class UserSessionCookie(SchemaBase):
    session_id: UUID
    identity_provider: IdentityProvider
    user_id: UUID | None = None


class UserSession(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    identity_provider: IdentityProvider
    user_id: UUID | None = None
    user_name: str | None = None
    created_at: datetime = datetime.now(tz=timezone.utc)


class GoogleUserSession(UserSession):
    identity_provider: IdentityProvider = IdentityProvider.GOOGLE
    state: str | None = None

    def model_post_init(self, __context) -> None:
        if not self.state:
            raise ValueError("Google state is missing")
