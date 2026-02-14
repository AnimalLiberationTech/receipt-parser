from datetime import datetime, timedelta

from src.adapters.db.cosmos_db_core import init_db_session
from src.schemas.common import TableName
from src.schemas.user_session import UserSession, UserSessionCookie

SESSION_VALIDITY_DAYS = 7 * 2


def validate_session(cookie: UserSessionCookie | None, logger) -> UserSession | None:
    if cookie:
        db_session = init_db_session(logger)
        db_session.use_table(TableName.USER_SESSION)
        session = db_session.read_one(
            str(cookie.session_id), partition_key=cookie.identity_provider
        )

        if session:
            created_at = datetime.fromisoformat(session["created_at"])
            now = datetime.now(tz=created_at.tzinfo)

            if created_at + timedelta(days=SESSION_VALIDITY_DAYS) < now:
                db_session.delete_one(session["id"], partition_key=session["user_id"])
            else:
                return UserSession.model_validate(session)

    return None
