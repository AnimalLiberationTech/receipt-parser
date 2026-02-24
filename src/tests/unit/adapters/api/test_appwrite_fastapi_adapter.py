"""
Unit tests for AppwriteFastAPIAdapter.

Tests cover scope construction (headers, query params, body), response translation,
and edge cases for both request and response handling.
"""

import asyncio
import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse

from src.adapters.api.appwrite_fastapi_adapter import AppwriteFastAPIAdapter

pytestmark = pytest.mark.asyncio


# Fixtures
@pytest.fixture
def simple_app():
    """Create a simple FastAPI app for testing."""
    app = FastAPI()

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/echo-headers")
    async def echo_headers(request):
        return {"headers": dict(request.headers)}

    @app.get("/echo-query")
    async def echo_query(param: str = None):
        return {"param": param}

    @app.post("/echo-body")
    async def echo_body(request):
        body = await request.json()
        return {"received": body}

    @app.post("/echo-json")
    async def echo_json():
        return {"data": "json_response"}

    @app.get("/text-response")
    async def text_response():
        return PlainTextResponse("plain text content")

    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")

    return app


@pytest.fixture
def adapter(simple_app):
    """Create an adapter with the simple test app."""
    return AppwriteFastAPIAdapter(simple_app)


@pytest.fixture
def mock_context():
    """Create a mock Appwrite context."""
    context = MagicMock()
    context.req = MagicMock()
    context.res = MagicMock()

    # Default request values
    context.req.method = "GET"
    context.req.path = "/health"
    context.req.url = "/health"
    context.req.headers = {}
    context.req.body = None

    # Default response behavior
    context.res.json = MagicMock(return_value={"status": "ok"})
    context.res.send = MagicMock(return_value="ok")

    return context


# Tests: Scope Construction


class TestScopeConstruction:
    """Tests for ASGI scope building from Appwrite context."""

    async def test_basic_scope_construction(self, adapter, mock_context):
        """Test basic ASGI scope is built correctly."""
        mock_context.req.method = "GET"
        mock_context.req.path = "/health"
        mock_context.req.url = "/health"
        mock_context.req.headers = {"content-type": "application/json"}

        # Capture scope by patching app call
        captured_scope = None

        async def capture_scope(scope, receive, send):
            nonlocal captured_scope
            captured_scope = scope
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b'{"status":"ok"}',
                }
            )

        adapter.app = AsyncMock(side_effect=capture_scope)

        await adapter.handle(mock_context)

        assert captured_scope["type"] == "http"
        assert captured_scope["asgi"]["version"] == "3.0"
        assert captured_scope["http_version"] == "1.1"
        assert captured_scope["method"] == "GET"
        assert captured_scope["path"] == "/health"
        assert captured_scope["scheme"] == "https"
        assert captured_scope["server"] == ("appwrite", 443)
        assert captured_scope["client"] == ("appwrite", 0)
        assert captured_scope["appwrite_context"] is mock_context

    async def test_headers_conversion_string_keys_values(self, adapter, mock_context):
        """Test headers with string keys and values."""
        mock_context.req.headers = {
            "content-type": "application/json",
            "authorization": "Bearer token123",
            "x-custom-header": "custom-value",
        }

        captured_scope = None

        async def capture_scope(scope, receive, send):
            nonlocal captured_scope
            captured_scope = scope
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [],
                }
            )
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_scope)

        await adapter.handle(mock_context)

        # Headers should be list of tuples with bytes
        headers_dict = {k.decode(): v.decode() for k, v in captured_scope["headers"]}
        assert headers_dict["content-type"] == "application/json"
        assert headers_dict["authorization"] == "Bearer token123"
        assert headers_dict["x-custom-header"] == "custom-value"

    async def test_headers_conversion_bytes_keys_values(self, adapter, mock_context):
        """Test headers with bytes keys and values."""
        mock_context.req.headers = {
            b"content-type": b"application/json",
            b"authorization": "Bearer token123",
        }

        captured_scope = None

        async def capture_scope(scope, receive, send):
            nonlocal captured_scope
            captured_scope = scope
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_scope)

        await adapter.handle(mock_context)

        # The adapter converts all values to str() first, so b"..." becomes "b'...'"
        headers_dict = {k.decode(): v.decode() for k, v in captured_scope["headers"]}
        assert headers_dict["content-type"] == "application/json"
        assert headers_dict["authorization"] == "Bearer token123"

    async def test_no_headers(self, adapter, mock_context):
        """Test when headers are None."""
        mock_context.req.headers = None

        captured_scope = None

        async def capture_scope(scope, receive, send):
            nonlocal captured_scope
            captured_scope = scope
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_scope)

        await adapter.handle(mock_context)

        assert captured_scope["headers"] == []

    async def test_empty_headers(self, adapter, mock_context):
        """Test when headers are empty dict."""
        mock_context.req.headers = {}

        captured_scope = None

        async def capture_scope(scope, receive, send):
            nonlocal captured_scope
            captured_scope = scope
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_scope)

        await adapter.handle(mock_context)

        assert captured_scope["headers"] == []

    async def test_query_string_simple(self, adapter, mock_context):
        """Test query string parsing from URL."""
        mock_context.req.url = "/echo-query?param=value123"

        captured_scope = None

        async def capture_scope(scope, receive, send):
            nonlocal captured_scope
            captured_scope = scope
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_scope)

        await adapter.handle(mock_context)

        assert captured_scope["query_string"] == b"param=value123"

    async def test_query_string_multiple_params(self, adapter, mock_context):
        """Test query string with multiple parameters."""
        mock_context.req.url = "/echo-query?param1=value1&param2=value2&key=value"

        captured_scope = None

        async def capture_scope(scope, receive, send):
            nonlocal captured_scope
            captured_scope = scope
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_scope)

        await adapter.handle(mock_context)

        assert captured_scope["query_string"] == b"param1=value1&param2=value2&key=value"

    async def test_query_string_none(self, adapter, mock_context):
        """Test when URL has no query string."""
        mock_context.req.url = "/health"

        captured_scope = None

        async def capture_scope(scope, receive, send):
            nonlocal captured_scope
            captured_scope = scope
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_scope)

        await adapter.handle(mock_context)

        assert captured_scope["query_string"] == b""

    async def test_query_string_with_special_chars(self, adapter, mock_context):
        """Test query string with special characters."""
        mock_context.req.url = "/echo-query?text=hello%20world&special=%3D%26%3F"

        captured_scope = None

        async def capture_scope(scope, receive, send):
            nonlocal captured_scope
            captured_scope = scope
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_scope)

        await adapter.handle(mock_context)

        assert captured_scope["query_string"] == b"text=hello%20world&special=%3D%26%3F"

    async def test_url_without_url_attribute(self, adapter, mock_context):
        """Test when context.req doesn't have url attribute."""
        del mock_context.req.url

        captured_scope = None

        async def capture_scope(scope, receive, send):
            nonlocal captured_scope
            captured_scope = scope
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_scope)

        await adapter.handle(mock_context)

        assert captured_scope["query_string"] == b""


# Tests: Request Body


class TestRequestBody:
    """Tests for receiving request body in various formats."""

    async def test_body_as_string(self, adapter, mock_context):
        """Test receiving body as string."""
        request_body = '{"key": "value"}'
        mock_context.req.body = request_body
        mock_context.req.method = "POST"
        mock_context.req.path = "/echo-body"

        captured_body = None

        async def capture_receive(scope, receive, send):
            message = await receive()
            nonlocal captured_body
            captured_body = message["body"]
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send({"type": "http.response.body", "body": b'{"ok": true}'})

        adapter.app = AsyncMock(side_effect=capture_receive)

        await adapter.handle(mock_context)

        assert captured_body == b'{"key": "value"}'

    async def test_body_as_bytes(self, adapter, mock_context):
        """Test receiving body as bytes."""
        request_body = b'{"key": "value"}'
        mock_context.req.body = request_body
        mock_context.req.method = "POST"

        captured_body = None

        async def capture_receive(scope, receive, send):
            message = await receive()
            nonlocal captured_body
            captured_body = message["body"]
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_receive)

        await adapter.handle(mock_context)

        assert captured_body == b'{"key": "value"}'

    async def test_body_as_dict(self, adapter, mock_context):
        """Test receiving body as dict (should be JSON-encoded)."""
        request_body = {"key": "value", "nested": {"inner": "data"}}
        mock_context.req.body = request_body
        mock_context.req.method = "POST"

        captured_body = None

        async def capture_receive(scope, receive, send):
            message = await receive()
            nonlocal captured_body
            captured_body = message["body"]
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_receive)

        await adapter.handle(mock_context)

        assert json.loads(captured_body) == request_body

    async def test_body_as_list(self, adapter, mock_context):
        """Test receiving body as list (should be JSON-encoded)."""
        request_body = [1, 2, 3, {"key": "value"}]
        mock_context.req.body = request_body
        mock_context.req.method = "POST"

        captured_body = None

        async def capture_receive(scope, receive, send):
            message = await receive()
            nonlocal captured_body
            captured_body = message["body"]
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_receive)

        await adapter.handle(mock_context)

        assert json.loads(captured_body) == request_body

    async def test_body_none(self, adapter, mock_context):
        """Test when body is None."""
        mock_context.req.body = None
        mock_context.req.method = "GET"

        captured_body = None

        async def capture_receive(scope, receive, send):
            message = await receive()
            nonlocal captured_body
            captured_body = message["body"]
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_receive)

        await adapter.handle(mock_context)

        assert captured_body == b""

    async def test_body_fallback_to_json_attribute(self, adapter, mock_context):
        """Test fallback to context.req.json when body is None."""
        mock_context.req.body = None
        mock_context.req.json = {"from": "json_attr"}
        mock_context.req.method = "POST"

        captured_body = None

        async def capture_receive(scope, receive, send):
            message = await receive()
            nonlocal captured_body
            captured_body = message["body"]
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_receive)

        await adapter.handle(mock_context)

        assert json.loads(captured_body) == {"from": "json_attr"}

    async def test_body_json_attribute_none(self, adapter, mock_context):
        """Test when both body and json attribute are None."""
        mock_context.req.body = None
        mock_context.req.json = None
        mock_context.req.method = "GET"

        captured_body = None

        async def capture_receive(scope, receive, send):
            message = await receive()
            nonlocal captured_body
            captured_body = message["body"]
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_receive)

        await adapter.handle(mock_context)

        assert captured_body == b""

    async def test_receive_message_structure(self, adapter, mock_context):
        """Test receive() returns correct ASGI message structure."""
        mock_context.req.body = b"test"
        mock_context.req.method = "POST"

        captured_message = None

        async def capture_receive(scope, receive, send):
            message = await receive()
            nonlocal captured_message
            captured_message = message
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_receive)

        await adapter.handle(mock_context)

        assert captured_message["type"] == "http.request"
        assert "body" in captured_message
        assert captured_message["more_body"] is False


# Tests: Response Translation


class TestResponseTranslation:
    """Tests for translating FastAPI responses to Appwrite context."""

    async def test_json_response_200(self, adapter, mock_context):
        """Test JSON response with 200 status code."""
        response_data = {"status": "ok", "data": 123}

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": json.dumps(response_data).encode(),
                }
            )

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        mock_context.res.json.assert_called_once()
        call_args = mock_context.res.json.call_args
        assert call_args[0][0] == response_data
        assert call_args[0][1] == 200

    async def test_json_response_400(self, adapter, mock_context):
        """Test JSON response with 400 status code."""
        response_data = {"error": "Bad request"}

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 400,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": json.dumps(response_data).encode(),
                }
            )

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        call_args = mock_context.res.json.call_args
        assert call_args[0][1] == 400

    async def test_json_response_500(self, adapter, mock_context):
        """Test JSON response with 500 status code."""
        response_data = {"error": "Internal server error"}

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 500,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": json.dumps(response_data).encode(),
                }
            )

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        call_args = mock_context.res.json.call_args
        assert call_args[0][1] == 500

    async def test_json_response_with_headers(self, adapter, mock_context):
        """Test JSON response preserves custom headers."""
        response_data = {"data": "test"}

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"x-custom-header", b"custom-value"),
                    ],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": json.dumps(response_data).encode(),
                }
            )

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        call_args = mock_context.res.json.call_args
        headers = call_args[0][2]
        assert headers["x-custom-header"] == "custom-value"
        assert headers["content-type"] == "application/json"

    async def test_text_response(self, adapter, mock_context):
        """Test plain text response."""
        response_text = "Plain text response"

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"text/plain")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": response_text.encode(),
                }
            )

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        mock_context.res.send.assert_called_once()
        call_args = mock_context.res.send.call_args
        assert call_args[0][0] == response_text
        assert call_args[0][1] == 200

    async def test_html_response(self, adapter, mock_context):
        """Test HTML response (text-based)."""
        response_html = "<html><body>Test</body></html>"

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"text/html")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": response_html.encode(),
                }
            )

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        call_args = mock_context.res.send.call_args
        assert call_args[0][0] == response_html

    async def test_empty_response_body(self, adapter, mock_context):
        """Test response with empty body."""

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 204,
                    "headers": [],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b"",
                }
            )

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        # 204 has no body, so neither json nor send should be called
        # or send should be called with empty string
        assert mock_context.res.json.called or mock_context.res.send.called

    async def test_large_json_response(self, adapter, mock_context):
        """Test handling of large JSON response."""
        large_data = {"items": [{"id": i, "value": f"item_{i}"} for i in range(1000)]}

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": json.dumps(large_data).encode(),
                }
            )

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        call_args = mock_context.res.json.call_args
        assert call_args[0][0] == large_data

    async def test_binary_response_without_json_content_type(self, adapter, mock_context):
        """Test binary response with non-JSON content type."""
        binary_data = b"\x89PNG\r\n\x1a\n"

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"image/png")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": binary_data,
                }
            )

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        # Binary data should be sent via send(), not json()
        mock_context.res.send.assert_called_once()

    async def test_response_with_bytes_headers(self, adapter, mock_context):
        """Test response header conversion from bytes to strings."""

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"x-test", b"value"),
                    ],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b'{"ok": true}',
                }
            )

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        call_args = mock_context.res.json.call_args
        headers = call_args[0][2]
        # Headers should be strings, not bytes
        assert isinstance(list(headers.keys())[0], str)
        assert isinstance(list(headers.values())[0], str)

    async def test_response_no_content_type(self, adapter, mock_context):
        """Test response without content-type header."""
        response_data = b"some data"

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": response_data,
                }
            )

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        # Without content-type, should use send() for text-like content
        mock_context.res.send.assert_called_once()


# Tests: Error Handling


class TestErrorHandling:
    """Tests for error handling in adapter."""

    async def test_app_raises_exception(self, adapter, mock_context):
        """Test adapter catches exception from app."""

        async def failing_app(scope, receive, send):
            raise ValueError("Test error in app")

        adapter.app = AsyncMock(side_effect=failing_app)

        await adapter.handle(mock_context)

        mock_context.res.json.assert_called_once()
        call_args = mock_context.res.json.call_args
        assert call_args[0][1] == 500  # status code
        assert "error" in call_args[0][0]
        assert "Internal server error" in call_args[0][0]["error"]

    async def test_app_raises_runtime_error(self, adapter, mock_context):
        """Test adapter catches RuntimeError from app."""

        async def failing_app(scope, receive, send):
            raise RuntimeError("Runtime error details")

        adapter.app = AsyncMock(side_effect=failing_app)

        await adapter.handle(mock_context)

        call_args = mock_context.res.json.call_args
        assert call_args[0][1] == 500
        assert "Runtime error details" in call_args[0][0]["detail"]

    async def test_invalid_json_response_body(self, adapter, mock_context):
        """Test handling of invalid JSON in response body."""
        invalid_json = b"not valid json {{"

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": invalid_json,
                }
            )

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        # When JSON is invalid, should fall back to send()
        mock_context.res.send.assert_called_once()

    async def test_invalid_utf8_response_body(self, adapter, mock_context):
        """Test handling of invalid UTF-8 in response body."""
        invalid_utf8 = b"\xff\xfe invalid"

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": invalid_utf8,
                }
            )

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        # Should fall back to send() with error-replace
        mock_context.res.send.assert_called_once()


# Tests: Edge Cases


class TestEdgeCases:
    """Tests for edge cases and unusual scenarios."""

    async def test_multiple_response_body_chunks(self, adapter, mock_context):
        """Test response with multiple body chunks."""
        chunk1 = b'{"part1": '
        chunk2 = b'"value", "part2": '
        chunk3 = b'"data"}'

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send({"type": "http.response.body", "body": chunk1})
            await send({"type": "http.response.body", "body": chunk2})
            await send({"type": "http.response.body", "body": chunk3})

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        call_args = mock_context.res.json.call_args
        response_data = call_args[0][0]
        assert response_data["part1"] == "value"
        assert response_data["part2"] == "data"

    async def test_response_no_body_sent(self, adapter, mock_context):
        """Test response where only http.response.start is sent."""

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            # No body sent

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        # Should handle gracefully without crashing
        assert mock_context.res.json.called or mock_context.res.send.called

    async def test_unicode_in_headers(self, adapter, mock_context):
        """Test headers with unicode characters (latin-1 compatible)."""
        mock_context.req.headers = {
            "x-custom": "café",
            "x-accent": "naïve",
        }

        captured_scope = None

        async def capture_scope(scope, receive, send):
            nonlocal captured_scope
            captured_scope = scope
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_scope)

        await adapter.handle(mock_context)

        # Headers should be properly encoded with latin-1
        headers_dict = {
            k.decode(): v.decode("latin-1") for k, v in captured_scope["headers"]
        }
        assert headers_dict["x-custom"] == "café"
        assert headers_dict["x-accent"] == "naïve"

    async def test_unicode_in_response(self, adapter, mock_context):
        """Test response with unicode data."""
        response_data = {
            "message": "Hello, 世界",
            "emoji": "🚀",
            "french": "café",
        }

        async def app_with_response(scope, receive, send):
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": json.dumps(response_data, ensure_ascii=False).encode("utf-8"),
                }
            )

        adapter.app = AsyncMock(side_effect=app_with_response)

        await adapter.handle(mock_context)

        call_args = mock_context.res.json.call_args
        assert call_args[0][0] == response_data

    async def test_very_large_body(self, adapter, mock_context):
        """Test handling of very large request body."""
        large_body = "x" * (10 * 1024 * 1024)  # 10MB
        mock_context.req.body = large_body
        mock_context.req.method = "POST"

        captured_body = None

        async def capture_receive(scope, receive, send):
            message = await receive()
            nonlocal captured_body
            captured_body = message["body"]
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        adapter.app = AsyncMock(side_effect=capture_receive)

        await adapter.handle(mock_context)

        assert len(captured_body) == len(large_body)

    async def test_all_http_methods(self, adapter, mock_context):
        """Test scope construction for different HTTP methods."""
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

        for method in methods:
            mock_context.req.method = method

            captured_scope = None

            async def capture_scope(scope, receive, send):
                nonlocal captured_scope
                captured_scope = scope
                await send({"type": "http.response.start", "status": 200, "headers": []})
                await send({"type": "http.response.body", "body": b""})

            adapter.app = AsyncMock(side_effect=capture_scope)

            await adapter.handle(mock_context)

            assert captured_scope["method"] == method

    async def test_consecutive_calls(self, adapter, mock_context):
        """Test adapter handles consecutive requests properly."""
        for i in range(3):
            mock_context.req.path = f"/health{i}"

            async def app_with_response(scope, receive, send):
                await send(
                    {
                        "type": "http.response.start",
                        "status": 200,
                        "headers": [(b"content-type", b"application/json")],
                    }
                )
                await send(
                    {
                        "type": "http.response.body",
                        "body": json.dumps({"request": i}).encode(),
                    }
                )

            adapter.app = AsyncMock(side_effect=app_with_response)

            mock_context.res.reset_mock()
            await adapter.handle(mock_context)

            assert mock_context.res.json.called
