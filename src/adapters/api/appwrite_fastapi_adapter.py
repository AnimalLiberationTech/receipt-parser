"""
Adapter to run FastAPI application within Appwrite function context.
Translates between Appwrite's context object and ASGI protocol.
"""

import json
import urllib.parse
from fastapi import FastAPI


class AppwriteFastAPIAdapter:
    """Adapter that bridges FastAPI ASGI app with Appwrite function context."""

    def __init__(self, app: FastAPI):
        """
        Initialize the adapter with the FastAPI app.

        Args:
            app: FastAPI application instance
        """
        self.app = app

    async def handle(self, context):
        """
        Handle Appwrite function context by routing through FastAPI.

        Args:
            context: Appwrite function context with req and res objects

        Returns:
            Response object from Appwrite context
        """
        # Build ASGI scope from Appwrite request
        headers = []
        for key, value in (context.req.headers or {}).items():
            key_lower = key.lower() if isinstance(key, str) else key.decode().lower()
            if isinstance(value, str):
                value_str = value
            elif isinstance(value, (bytes, bytearray)):
                value_str = bytes(value).decode("latin-1", errors="replace")
            else:
                value_str = str(value)
            headers.append((key_lower.encode("latin-1"), value_str.encode("latin-1")))

        query_string = b""
        if hasattr(context.req, "url") and "?" in context.req.url:
            query_string = context.req.url.split("?", 1)[1].encode("latin-1")

        if not query_string:
            query_params = getattr(context.req, "query", None)
            if isinstance(query_params, (bytes, bytearray)):
                query_string = bytes(query_params)
            elif isinstance(query_params, str):
                query_string = query_params.lstrip("?").encode("utf-8")
            elif isinstance(query_params, (dict, list, tuple)):
                query_string = urllib.parse.urlencode(query_params, doseq=True).encode("ascii")

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.0"},
            "http_version": "1.1",
            "method": context.req.method,
            "scheme": "https",
            "path": context.req.path,
            "query_string": query_string,
            "headers": headers,
            "server": ("appwrite", 443),
            "client": ("appwrite", 0),
            "appwrite_context": context,  # Pass context for logger
        }

        # Capture response
        response_started = False
        response_body = b""
        response_status = 200
        response_headers = []

        async def receive():
            """Provide request body to ASGI app."""
            body = b""
            if hasattr(context.req, "body"):
                if isinstance(context.req.body, str):
                    body = context.req.body.encode("utf-8")
                elif isinstance(context.req.body, bytes):
                    body = context.req.body
                elif isinstance(context.req.body, (dict, list)):
                    body = json.dumps(context.req.body).encode("utf-8")

            if not body and hasattr(context.req, "json"):
                req_json = context.req.json
                if isinstance(req_json, (dict, list)):
                    body = json.dumps(req_json).encode("utf-8")

            return {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }

        async def send(message):
            """Capture response from ASGI app."""
            nonlocal response_started, response_status, response_headers, response_body

            if message["type"] == "http.response.start":
                response_started = True
                response_status = message["status"]
                response_headers = message.get("headers", [])
            elif message["type"] == "http.response.body":
                response_body += message.get("body", b"")

        # Call FastAPI app
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            # Error during app execution
            return context.res.json(
                {"error": "Internal server error", "detail": str(e)},
                500,
                {"Content-Type": "application/json"},
            )

        # Convert response headers dict
        response_headers_dict = {}
        for key, value in response_headers:
            key_str = key.decode("latin-1") if isinstance(key, bytes) else key
            value_str = value.decode("latin-1") if isinstance(value, bytes) else value
            response_headers_dict[key_str] = value_str

        # Return response via Appwrite context
        # Header names are case-insensitive; build a lowercased view for lookup
        lower_headers = {str(k).lower(): v for k, v in response_headers_dict.items()}
        content_type = lower_headers.get("content-type", "")

        if "application/json" in content_type:
            try:
                data = json.loads(response_body.decode("utf-8"))
                return context.res.json(data, response_status, response_headers_dict)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        # Return as text/binary
        return context.res.send(
            response_body.decode("utf-8", errors="replace"),
            response_status,
            response_headers_dict,
        )
