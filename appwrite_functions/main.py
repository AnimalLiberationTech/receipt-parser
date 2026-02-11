import json
import os
import sys

# needed when the function is deployed and 'src' is copied next to main.py
current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)

# Fallback for local development where 'src' is at the project root (one level up)
if not os.path.exists(os.path.join(current_dir, "src")):
    sys.path.append(os.path.abspath(os.path.join(current_dir, "../")))

from src.handlers.add_barcodes import add_barcodes_handler
from src.handlers.link_shop import link_shop_handler
from src.handlers.parse_from_url import parse_from_url_handler
from src.handlers.shops import shops_handler


class AppwriteLogger:
    def __init__(self, context):
        self.context = context

    def info(self, msg, *args):
        self.context.log(str(msg) % args if args else str(msg))

    def warning(self, msg, *args):
        self.context.log(f"WARNING: {str(msg) % args if args else str(msg)}")

    def error(self, msg, *args):
        self.context.error(str(msg) % args if args else str(msg))


def parse_json_body(func):
    """Decorator that parses JSON body and passes it to the handler."""
    def wrapper(context, logger):
        try:
            if isinstance(context.req.body, str):
                body = json.loads(context.req.body)
            else:
                body = context.req.body
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            logger.error(f"Error parsing body ({type(e).__name__}): {e}")
            return context.res.json({"msg": "Invalid JSON body"}, 400)

        status, response = func(body, logger)
        return context.res.json(response, status.value)
    return wrapper


@parse_json_body
def handle_parse_from_url(body, logger):
    url = body.get("url")
    user_id = body.get("user_id")
    return parse_from_url_handler(url, user_id, logger)


@parse_json_body
def handle_link_shop(body, logger):
    url = body.get("url")
    user_id = body.get("user_id")
    receipt_id = body.get("receipt_id")
    return link_shop_handler(url, user_id, receipt_id, logger)


@parse_json_body
def handle_add_barcodes(body, logger):
    shop_id = body.get("shop_id")
    items = body.get("items", [])
    return add_barcodes_handler(shop_id, items, logger)


def handle_health(context, logger):
    return context.res.json({"status": "ok"}, 200)


def handle_shops(context, logger):
    """Handle GET /shops - returns shops filtered by query params."""
    query_params = dict(context.req.query) if context.req.query else {}
    status, response = shops_handler(query_params, logger)
    return context.res.json(response, status.value)


GET = "GET"
POST = "POST"

ROUTES = {
    (POST, "/parse"): handle_parse_from_url,
    (POST, "/parse-from-url"): handle_parse_from_url,
    (POST, "/link-shop"): handle_link_shop,
    (POST, "/add-barcodes"): handle_add_barcodes,
    (GET, "/"): handle_health,
    (GET, "/health"): handle_health,
    (GET, "/shops"): handle_shops,
}


def main(context):
    logger = AppwriteLogger(context)

    method = context.req.method
    path = context.req.path

    # Normalize path (remove trailing slash)
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    handler = ROUTES.get((method, path))

    if handler:
        return handler(context, logger)

    logger.warning(f"Route not found: {method} {path}")
    return context.res.json({"error": "Not found", "path": path, "method": method}, 404)

