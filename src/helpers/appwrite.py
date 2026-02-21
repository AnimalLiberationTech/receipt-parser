import json
from typing import Callable

from src.db.appwrite_db_api import AppwriteDbApi
from src.schemas.common import ApiResponse

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, x-appwrite-key",
}


class AppwriteLogger:
    """Logger adapter for Appwrite context."""

    def __init__(self, context):
        self.context = context

    def info(self, msg, *args):
        self.context.log(str(msg) % args if args else str(msg))

    def log(self, msg, *args):
        self.context.log(str(msg) % args if args else str(msg))

    def warning(self, msg, *args):
        self.context.log(f"WARNING: {str(msg) % args if args else str(msg)}")

    def error(self, msg, *args):
        self.context.error(str(msg) % args if args else str(msg))


def build_db_api(context, logger):
    """Build an AppwriteDbApi instance from Appwrite context."""
    x_appwrite_key = context.req.headers.get("x-appwrite-key")
    return AppwriteDbApi(x_appwrite_key, logger)


def with_db_api(func: Callable[..., ApiResponse]) -> Callable[..., ApiResponse]:
    """Decorator that injects db_api into Appwrite function handlers."""

    def wrapper(context, logger) -> ApiResponse:
        return func(context, logger, build_db_api(context, logger))

    return wrapper


def parse_json_body(func):
    """Decorator that parses JSON body and passes it to the handler."""

    def wrapper(context, logger, *args, **kwargs):
        try:
            if isinstance(context.req.body, str):
                body = json.loads(context.req.body)
            else:
                body = context.req.body
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            logger.error(f"Error parsing body ({type(e).__name__}): {e}")
            return context.res.json({"msg": "Invalid JSON body"}, 400, CORS_HEADERS)

        result = func(body, logger, *args, **kwargs)

        # Handle ApiResponse objects
        if isinstance(result, ApiResponse):
            return context.res.json(result.model_dump(), result.status_code, CORS_HEADERS)
        # Handle tuple format: (status, response)
        else:
            status, response = result
            return context.res.json(response, status.value, CORS_HEADERS)

    return wrapper
