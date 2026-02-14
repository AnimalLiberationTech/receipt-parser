import json
import os
import sys
from http import HTTPStatus

# Add parent directory to path for src imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure.functions import FunctionApp, AuthLevel, HttpRequest, HttpResponse

from src.adapters.auth.google_auth import GoogleAuth, GOOGLE_CALLBACK_URI
from src.handlers.add_barcodes import add_barcodes_handler
from src.handlers.home import home_handler
from src.handlers.link_shop import link_shop_handler
from src.handlers.parse_from_url import parse_from_url_handler
from src.helpers.azure_function import (
    get_form_data,
    build_response,
    login_page_link,
    format_session_cookie,
    get_cookies,
    format_user_id_cookie,
    format_invalid_user_id_cookie,
)
from src.helpers.logging import set_logger
from src.helpers.session import validate_session
from src.schemas.user_session import GoogleUserSession

logger = set_logger()
app = FunctionApp(http_auth_level=AuthLevel.ANONYMOUS)


@app.route("parse-from-url", methods=["POST"])
def parse_from_url(req: HttpRequest) -> HttpResponse:
    if not validate_session(get_cookies(req.headers, logger), logger):
        HttpResponse(status_code=HTTPStatus.UNAUTHORIZED)

    logger.info(req.form.to_dict())
    url, user_id = get_form_data(req, "url", "user_id")
    return build_response(*parse_from_url_handler(url, user_id, logger))


@app.route("link-shop", methods=["POST"])
def link_shop(req: HttpRequest) -> HttpResponse:
    if not validate_session(get_cookies(req.headers, logger), logger):
        HttpResponse(status_code=HTTPStatus.UNAUTHORIZED)

    logger.info(req.form.to_dict())
    url, user_id, receipt_id = get_form_data(req, "url", "user_id", "receipt_id")
    return build_response(*link_shop_handler(url, user_id, receipt_id, logger))


@app.route("add-barcodes", methods=["POST"])
def add_barcodes(req: HttpRequest) -> HttpResponse:
    if not validate_session(get_cookies(req.headers, logger), logger):
        HttpResponse(status_code=HTTPStatus.UNAUTHORIZED)

    logger.info(req.form.to_dict())
    shop_id, items = get_form_data(req, "shop_id", "items")
    return build_response(*add_barcodes_handler(shop_id, json.loads(items), logger))


@app.route("home", methods=["GET"])
def home(req: HttpRequest) -> HttpResponse:
    if not validate_session(get_cookies(req.headers, logger), logger):
        return login_page_link()

    return build_response(*home_handler(), mimetype="text/html")


@app.route("google-login", methods=["GET"])
def google_login(req: HttpRequest) -> HttpResponse:  # pylint: disable=unused-argument
    google_auth = GoogleAuth(logger)

    auth_url, cookie = google_auth.create_session()
    return HttpResponse(
        status_code=HTTPStatus.FOUND,
        headers={
            "Location": auth_url,
            "Set-Cookie": format_session_cookie(cookie),
        },
    )


@app.route(GOOGLE_CALLBACK_URI, methods=["GET"])
def google_login_callback(
    req: HttpRequest,
) -> HttpResponse:
    cookies = get_cookies(req.headers, logger)
    google_auth = GoogleAuth(logger)
    session: GoogleUserSession = google_auth.get_new_session(cookies.session_id)

    logger.info(req.params.get("state"))
    if not session or session.state != req.params["state"]:
        return HttpResponse(status_code=HTTPStatus.BAD_REQUEST)

    google_auth.verify_token(req.url)
    if not google_auth.user:
        return HttpResponse(status_code=HTTPStatus.UNAUTHORIZED)

    session = google_auth.update_session(session, google_auth.user)

    return HttpResponse(
        status_code=HTTPStatus.FOUND,
        headers={
            "Location": "/home",
            "Set-Cookie": format_user_id_cookie(session.user_id),
        },
    )


@app.route("logout", methods=["GET"])
def logout(req: HttpRequest) -> HttpResponse:  # pylint: disable=unused-argument
    return HttpResponse(
        status_code=HTTPStatus.FOUND,
        headers={
            "Location": "/home",
            "Set-Cookie": format_invalid_user_id_cookie(),
        },
    )


