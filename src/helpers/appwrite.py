import json
import os
from typing import Callable
from urllib.parse import urlencode

import requests

from src.schemas.common import ApiResponse

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, x-appwrite-key",
}


def appwrite_db_api(
    uri: str,
    method: str,
    payload: dict | None,
    x_appwrite_key: str,
    log,
    query: dict | None = None,
) -> dict | None:
    payload = payload or {}
    headers = {
        "x-appwrite-key": x_appwrite_key,
        "x-appwrite-project": os.environ.get("APPWRITE_FUNCTION_PROJECT_ID"),
    }
    api_endpoint = os.environ["APPWRITE_FUNCTION_API_ENDPOINT"]
    # pbapi function call
    try:
        path = uri
        if query:
            separator = "&" if "?" in path else "?"
            path = f"{path}{separator}{urlencode(query, doseq=True)}"
        execution_payload = {
            "method": method,
            "path": path,
            "body": json.dumps(payload),
            "headers": {"content-type": "application/json"},
        }
        response = requests.post(
            f"{api_endpoint}/functions/pbapi/executions",
            json=execution_payload,
            headers=headers,
            timeout=10,
        )
        if response.status_code in [200, 201]:
            try:
                result = response.json()
                # Appwrite returns an execution object, we want the responseBody
                if "responseBody" in result:
                    try:
                        return json.loads(result["responseBody"])
                    except (ValueError, json.JSONDecodeError):
                        return result["responseBody"]
                return result
            except (ValueError, json.JSONDecodeError) as e:
                log.error(f"Failed to parse JSON response from pbapi: {str(e)}")
                return None

        log.error(f"Error calling pbapi: {response.status_code} - {response.text}")
    except requests.exceptions.Timeout:
        log.error("Timeout calling pbapi")
    except requests.exceptions.ConnectionError:
        log.error("Connection error calling pbapi")
    except requests.exceptions.RequestException as e:
        log.error(f"Request exception calling pbapi: {str(e)}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        log.error(f"Unexpected exception calling pbapi: {str(e)}")

    return None


class AppwriteLogger:
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
    x_appwrite_key = context.req.headers.get("x-appwrite-key")

    def init_db_api(
        uri: str,
        method: str,
        payload: dict | None = None,
        query: dict | None = None,
    ) -> dict | None:
        return appwrite_db_api(uri, method, payload, x_appwrite_key, logger, query)

    return init_db_api


def with_db_api(func: Callable[..., ApiResponse]) -> Callable[..., ApiResponse]:
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
