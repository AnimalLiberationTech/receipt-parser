"""Unit tests for src/helpers/appwrite.py"""

import json
import os
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any
from unittest import TestCase
from unittest.mock import MagicMock, patch

from src.db.appwrite_db_api import AppwriteDbApi
from src.helpers.appwrite import (
    AppwriteLogger,
    build_db_api,
    with_db_api,
    parse_json_body,
    CORS_HEADERS,
)
from src.schemas.common import ApiResponse


@dataclass
class MockRequest:
    method: str = "POST"
    body: Any = None
    headers: dict = field(default_factory=dict)
    query: dict = field(default_factory=dict)
    path: str = "/"


@dataclass
class MockResponse:
    _body: str = ""
    _status: int = 200
    _headers: dict = field(default_factory=dict)

    def send(self, body: str, status: int = 200, headers: dict = None):
        self._body = body
        self._status = status
        self._headers = headers or {}
        return self

    def json(self, data: dict, status: int = 200, headers: dict = None):
        self._body = json.dumps(data, indent=2)
        self._status = status
        self._headers = {"content-type": "application/json", **(headers or {})}
        return self

    def empty(self):
        return self.send("", 204)


@dataclass
class MockContext:
    req: MockRequest
    res: MockResponse = field(default_factory=MockResponse)

    def log(self, msg):
        print(f"[LOG] {msg}")

    def error(self, msg):
        print(f"[ERROR] {msg}")


class TestCORSHeaders(TestCase):
    """Test CORS_HEADERS constant."""

    def test_cors_headers_present(self):
        """Test that CORS_HEADERS constant is defined correctly."""
        self.assertIn("Access-Control-Allow-Origin", CORS_HEADERS)
        self.assertIn("Access-Control-Allow-Methods", CORS_HEADERS)
        self.assertIn("Access-Control-Allow-Headers", CORS_HEADERS)

    def test_cors_headers_values(self):
        """Test CORS_HEADERS values."""
        self.assertEqual(CORS_HEADERS["Access-Control-Allow-Origin"], "*")
        self.assertIn("GET", CORS_HEADERS["Access-Control-Allow-Methods"])
        self.assertIn("POST", CORS_HEADERS["Access-Control-Allow-Methods"])
        self.assertIn("x-appwrite-key", CORS_HEADERS["Access-Control-Allow-Headers"])


class TestAppwriteLogger(TestCase):
    """Test AppwriteLogger class."""

    def setUp(self):
        self.mock_context = MockContext(req=MockRequest())

    def test_logger_init(self):
        """Test AppwriteLogger initialization."""
        logger = AppwriteLogger(self.mock_context)
        self.assertEqual(logger.context, self.mock_context)

    def test_logger_info(self):
        """Test logger.info() method."""
        logger = AppwriteLogger(self.mock_context)
        logger.info("Test info message")
        # Should not raise exception

    def test_logger_log(self):
        """Test logger.log() method."""
        logger = AppwriteLogger(self.mock_context)
        logger.log("Test log message")
        # Should not raise exception

    def test_logger_warning(self):
        """Test logger.warning() method."""
        logger = AppwriteLogger(self.mock_context)
        logger.warning("Test warning message")
        # Should not raise exception

    def test_logger_error(self):
        """Test logger.error() method."""
        logger = AppwriteLogger(self.mock_context)
        logger.error("Test error message")
        # Should not raise exception

    def test_logger_with_formatting(self):
        """Test logger with % formatting."""
        logger = AppwriteLogger(self.mock_context)
        logger.info("Test %s message", "formatted")
        logger.warning("Warning %d", 123)
        logger.error("Error %s %s", "test", "data")
        # Should not raise exceptions


class TestBuildDbApi(TestCase):
    """Test build_db_api function."""

    def setUp(self):
        os.environ["APPWRITE_FUNCTION_PROJECT_ID"] = "test-project"
        os.environ["APPWRITE_FUNCTION_API_ENDPOINT"] = "http://localhost"

    def test_build_db_api_with_key(self):
        """Test build_db_api creates AppwriteDbApi with x-appwrite-key."""
        context = MockContext(req=MockRequest(headers={"x-appwrite-key": "test-api-key"}))
        logger = MagicMock()

        db_api = build_db_api(context, logger)

        self.assertIsInstance(db_api, AppwriteDbApi)

    def test_build_db_api_without_key(self):
        """Test build_db_api with missing x-appwrite-key."""
        context = MockContext(req=MockRequest(headers={}))
        logger = MagicMock()

        db_api = build_db_api(context, logger)

        self.assertIsInstance(db_api, AppwriteDbApi)

    def test_build_db_api_extracts_header(self):
        """Test build_db_api extracts x-appwrite-key from headers."""
        context = MockContext(
            req=MockRequest(
                headers={
                    "x-appwrite-key": "secret-key-123",
                    "content-type": "application/json",
                }
            )
        )
        logger = MagicMock()

        db_api = build_db_api(context, logger)

        self.assertIsInstance(db_api, AppwriteDbApi)


class TestWithDbApiDecorator(TestCase):
    """Test with_db_api decorator."""

    def setUp(self):
        os.environ["APPWRITE_FUNCTION_PROJECT_ID"] = "test-project"
        os.environ["APPWRITE_FUNCTION_API_ENDPOINT"] = "http://localhost"

    def test_decorator_injects_db_api(self):
        """Test that with_db_api decorator injects db_api parameter."""

        @with_db_api
        def test_handler(context, logger, db_api):
            return ApiResponse(
                status_code=HTTPStatus.OK,
                detail="Success",
                data={"db_api_type": type(db_api).__name__},
            )

        context = MockContext(req=MockRequest(headers={"x-appwrite-key": "test-key"}))
        logger = MagicMock()

        result = test_handler(context, logger)

        self.assertIsInstance(result, ApiResponse)
        self.assertEqual(result.status_code, HTTPStatus.OK)
        self.assertEqual(result.data["db_api_type"], "AppwriteDbApi")

    def test_decorator_returns_api_response(self):
        """Test that decorated function returns ApiResponse."""

        @with_db_api
        def test_handler(context, logger, db_api):
            return ApiResponse(
                status_code=HTTPStatus.CREATED,
                detail="Created",
            )

        context = MockContext(req=MockRequest(headers={"x-appwrite-key": "test-key"}))
        logger = MagicMock()

        result = test_handler(context, logger)

        self.assertEqual(result.status_code, HTTPStatus.CREATED)
        self.assertEqual(result.detail, "Created")


class TestParseJsonBodyDecorator(TestCase):
    """Test parse_json_body decorator."""

    def test_decorator_parses_json_string_body(self):
        """Test parse_json_body parses JSON string."""

        @parse_json_body
        def test_handler(body, logger):
            return ApiResponse(status_code=HTTPStatus.OK, detail="Parsed", data=body)

        context = MockContext(
            req=MockRequest(body=json.dumps({"key": "value", "number": 123}))
        )
        logger = MagicMock()

        result = test_handler(context, logger)

        self.assertEqual(result._status, HTTPStatus.OK)
        response_data = json.loads(result._body)
        self.assertEqual(response_data["data"]["key"], "value")
        self.assertEqual(response_data["data"]["number"], 123)

    def test_decorator_handles_dict_body(self):
        """Test parse_json_body with dict body."""

        @parse_json_body
        def test_handler(body, logger):
            return ApiResponse(status_code=HTTPStatus.OK, detail="Parsed", data=body)

        context = MockContext(req=MockRequest(body={"already": "dict"}))
        logger = MagicMock()

        result = test_handler(context, logger)

        self.assertEqual(result._status, HTTPStatus.OK)
        response_data = json.loads(result._body)
        self.assertEqual(response_data["data"]["already"], "dict")

    def test_decorator_handles_invalid_json(self):
        """Test parse_json_body with invalid JSON."""

        @parse_json_body
        def test_handler(body, logger):
            # Should not be called
            return ApiResponse(status_code=HTTPStatus.OK, detail="Should not reach")

        context = MockContext(req=MockRequest(body="invalid {json"))
        logger = MagicMock()

        result = test_handler(context, logger)

        # Should return error response from decorator
        self.assertEqual(result._status, 400)
        self.assertIn("Invalid JSON body", result._body)

    def test_decorator_includes_cors_headers_on_error(self):
        """Test parse_json_body includes CORS headers on JSON error."""

        @parse_json_body
        def test_handler(body, logger):
            return ApiResponse(status_code=HTTPStatus.OK, detail="OK")

        context = MockContext(req=MockRequest(body="invalid json {"))
        logger = MagicMock()

        result = test_handler(context, logger)

        self.assertIn("Access-Control-Allow-Origin", result._headers)
        self.assertEqual(result._headers["Access-Control-Allow-Origin"], "*")

    def test_decorator_with_api_response_return(self):
        """Test parse_json_body with ApiResponse return value."""

        @parse_json_body
        def test_handler(body, logger):
            return ApiResponse(
                status_code=HTTPStatus.CREATED, detail="Item created", data={"id": 123}
            )

        context = MockContext(req=MockRequest(body=json.dumps({"name": "test"})))
        logger = MagicMock()

        result = test_handler(context, logger)

        self.assertEqual(result._status, HTTPStatus.CREATED)
        self.assertIn("Item created", result._body)
        self.assertIn("Access-Control-Allow-Origin", result._headers)
        self.assertEqual(result._headers["Access-Control-Allow-Origin"], "*")

    def test_decorator_with_tuple_return(self):
        """Test parse_json_body with (status, response) tuple return."""

        @parse_json_body
        def test_handler(body, logger):
            # Return tuple format (status, response)
            return (HTTPStatus.OK, {"msg": "success", "data": body})

        context = MockContext(req=MockRequest(body=json.dumps({"test": "data"})))
        logger = MagicMock()

        result = test_handler(context, logger)

        self.assertEqual(result._status, HTTPStatus.OK)
        self.assertIn("success", result._body)
        self.assertIn("Access-Control-Allow-Origin", result._headers)
        self.assertEqual(result._headers["Access-Control-Allow-Origin"], "*")

    def test_decorator_passes_body_to_handler(self):
        """Test that parsed body is passed to handler."""

        received_body = {}

        @parse_json_body
        def test_handler(body, logger):
            nonlocal received_body
            received_body = body
            return ApiResponse(status_code=HTTPStatus.OK, detail="OK")

        context = MockContext(
            req=MockRequest(body=json.dumps({"user_id": "123", "amount": 99.99}))
        )
        logger = MagicMock()

        test_handler(context, logger)

        self.assertEqual(received_body["user_id"], "123")
        self.assertEqual(received_body["amount"], 99.99)

    def test_decorator_logs_json_error(self):
        """Test that decorator logs JSON parsing errors."""

        @parse_json_body
        def test_handler(body, logger):
            return ApiResponse(status_code=HTTPStatus.OK, detail="OK")

        context = MockContext(req=MockRequest(body="not valid json"))
        logger = MagicMock()

        test_handler(context, logger)

        # Verify logger.error was called
        logger.error.assert_called_once()
        call_args = str(logger.error.call_args)
        self.assertIn("JSONDecodeError", call_args)

    def test_decorator_with_extra_args(self):
        """Test parse_json_body decorator with extra *args and **kwargs."""

        @parse_json_body
        def test_handler(body, logger, *args, **kwargs):
            return ApiResponse(
                status_code=HTTPStatus.OK,
                detail="OK",
                data={"args": len(args), "kwargs": len(kwargs)},
            )

        context = MockContext(req=MockRequest(body=json.dumps({"test": "data"})))
        logger = MagicMock()

        result = test_handler(context, logger, "extra_arg", extra_kwarg="value")

        self.assertEqual(result._status, HTTPStatus.OK)
