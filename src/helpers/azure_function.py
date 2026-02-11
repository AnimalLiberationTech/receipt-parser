import json
from collections.abc import Mapping
from http import HTTPStatus
from http.cookies import SimpleCookie
from uuid import UUID

from azure.functions import HttpRequest, HttpResponse

from adapters.rest import fastapi_routes
from src.helpers.common import get_template_path
from src.helpers.session import SESSION_VALIDITY_DAYS
from src.schemas.user_identity import IdentityProvider
from src.schemas.user_session import UserSessionCookie

SESSION_COOKIE_NAME = "session_key"


def get_form_data(req: HttpRequest, *args: str) -> tuple[str, ...]:
    return tuple(fastapi_router.get(val).strip() for val in args)


def build_response(
    status: int, body: str | dict, mimetype: str = "application/json"
) -> HttpResponse:
    return HttpResponse(
        body=body if isinstance(body, str) else json.dumps(body),
        status_code=status,
        mimetype=mimetype,
        headers={"access-control-allow-origin": "*"},
    )


def get_cookies(headers: Mapping, logger) -> UserSessionCookie | None:
    c = SimpleCookie()
    c.load(headers.get("Cookie", ""))
    try:
        provider, session_id = c[SESSION_COOKIE_NAME].value.split("_", 1)
        return UserSessionCookie(
            session_id=UUID(session_id),
            identity_provider=IdentityProvider.get(provider),
            user_id=UUID(c["user_id"].value) if c.get("user_id") else None,
        )
    except (KeyError, ValueError) as e:
        logger.error(f"Failed to parse cookies: {e}")
        return None


def format_cookie(key: str, value: str, valid=True) -> str:
    max_age = 60 * 60 * 24 * SESSION_VALIDITY_DAYS
    return f"{key}={value}; Max-Age={max_age if valid else 0}; Path=/; Secure"


def format_session_cookie(cookie: UserSessionCookie) -> str:
    value = f"{cookie.identity_provider.value}_{cookie.session_id}"
    return format_cookie(SESSION_COOKIE_NAME, value)


def format_user_id_cookie(user_id: UUID) -> str:
    return format_cookie("user_id", str(user_id))


def format_invalid_user_id_cookie() -> str:
    return format_cookie("user_id", "", valid=False)


def login_page_link() -> HttpResponse:
    with open(get_template_path("login-en.html"), "r", encoding="utf8") as file:
        return build_response(HTTPStatus.UNAUTHORIZED, file.read(), mimetype="text/html")
