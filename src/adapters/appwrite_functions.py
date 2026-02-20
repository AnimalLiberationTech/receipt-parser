import os
from http import HTTPStatus
from uuid import UUID

import sys

current_dir = os.path.dirname(__file__)  # src/adapters/
base_dir = os.path.abspath(os.path.join(current_dir, "../../"))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from src.adapters.doppler import load_doppler_secrets
from src.handlers.add_barcodes import add_barcodes_handler
from src.handlers.link_shop import link_shop_handler
from src.handlers.parse_from_url import parse_from_url_handler
from src.handlers.shops import shops_handler
from src.helpers.appwrite import (
    CORS_HEADERS,
    AppwriteLogger,
    with_db_api,
    parse_json_body,
)
from src.schemas.common import OsmType, ApiResponse


@with_db_api
@parse_json_body
def handle_parse_from_url(body, logger, db_api) -> ApiResponse:
    url = body.get("url")
    if not url:
        return ApiResponse(status_code=HTTPStatus.BAD_REQUEST, detail="URL is required")

    try:
        user_id = UUID(body.get("user_id"))
    except ValueError:
        return ApiResponse(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid user ID")

    return parse_from_url_handler(url, user_id, logger, db_api)


@with_db_api
@parse_json_body
def handle_link_shop(body, logger, db_api) -> ApiResponse:
    try:
        osm_type = OsmType(body.get("osm_type"))
    except ValueError:
        return ApiResponse(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid OSM type")

    try:
        osm_key = int(body.get("osm_key"))
    except ValueError:
        return ApiResponse(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid OSM key")

    receipt_id = body.get("receipt_id")
    return link_shop_handler(osm_type, osm_key, receipt_id, logger, db_api)


@parse_json_body
def handle_add_barcodes(body, logger):
    shop_id = body.get("shop_id")
    items = body.get("items", [])
    return add_barcodes_handler(shop_id, items, logger)


def handle_health(context, logger):
    return context.res.json({"status": "ok"}, 200, CORS_HEADERS)


def handle_options(context, logger):
    """Handle OPTIONS requests for CORS preflight."""
    return context.res.send("", 204, CORS_HEADERS)


def handle_shops(context, logger):
    """Handle GET /shops - returns shops filtered by query params."""
    query_params = dict(context.req.query) if context.req.query else {}
    response: ApiResponse = shops_handler(query_params, logger)
    return context.res.json(response.model_dump(), response.status_code, CORS_HEADERS)


GET = "GET"
POST = "POST"
OPTIONS = "OPTIONS"

ROUTES = {
    (POST, "/parse"): handle_parse_from_url,
    (POST, "/link-shop"): handle_link_shop,
    (POST, "/add-barcodes"): handle_add_barcodes,
    (GET, "/"): handle_health,
    (GET, "/health"): handle_health,
    (GET, "/shops"): handle_shops,
    (OPTIONS, "/parse"): handle_options,
    (OPTIONS, "/link-shop"): handle_options,
    (OPTIONS, "/add-barcodes"): handle_options,
    (OPTIONS, "/shops"): handle_options,
}


def main(context):
    logger = AppwriteLogger(context)

    load_doppler_secrets()

    method = context.req.method
    path = context.req.path

    # Normalize path (remove trailing slash)
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    handler = ROUTES.get((method, path))

    if handler:
        return handler(context, logger)

    logger.warning(f"Route not found: {method} {path}")
    return context.res.json(
        {"error": "Not found", "path": path, "method": method}, 404, CORS_HEADERS
    )
