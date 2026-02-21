import json
import sys
import os
from dataclasses import dataclass, field
from typing import Any
from unittest import TestCase

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))


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


class TestAppwrite(TestCase):

    def test_decorator_chain(self) -> None:
        """Test that decorator chain works correctly."""

        os.environ.setdefault("ENV_NAME", "dev")
        os.environ.setdefault("APPWRITE_FUNCTION_PROJECT_ID", "test-project")
        os.environ.setdefault("APPWRITE_FUNCTION_API_ENDPOINT", "http://localhost")

        from src.adapters.api.appwrite_functions import (
            handle_parse_from_url,
            handle_link_shop,
            handle_add_barcodes,
        )

        print(
            "\n=== Testing handle_parse_from_url (with @with_db_api + @parse_json_body) ==="
        )
        context = MockContext(
            req=MockRequest(
                method="POST",
                path="/parse",
                body=json.dumps(
                    {
                        "url": "https://example.com",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",  # Valid UUID
                    }
                ),
                headers={"x-appwrite-key": "test-key"},
            )
        )

        try:
            response = handle_parse_from_url(context, context)
            print(f"✓ Decorator chain works! Status: {response._status}")
            print(f"  Headers: {list(response._headers.keys())}")
            assert "Access-Control-Allow-Origin" in response._headers
            print("✓ CORS headers present")
        except AttributeError as e:
            print(f"✗ FAILED: {e}")
            raise

        print("\n=== Testing handle_link_shop (with @with_db_api + @parse_json_body) ===")
        context = MockContext(
            req=MockRequest(
                method="POST",
                path="/link-shop",
                body=json.dumps(
                    {
                        "osm_type": "node",  # Valid OsmType
                        "osm_key": 123,  # Integer OSM key
                        "receipt_id": "test-receipt-id",
                    }
                ),
                headers={"x-appwrite-key": "test-key"},
            )
        )

        try:
            response = handle_link_shop(context, context)
            print(f"✓ Decorator works! Status: {response._status}")
            assert "Access-Control-Allow-Origin" in response._headers
            print("✓ CORS headers present")
        except AttributeError as e:
            print(f"✗ FAILED: {e}")
            raise

        print("\n=== Testing handle_add_barcodes (with @parse_json_body only) ===")
        context = MockContext(
            req=MockRequest(
                method="POST",
                path="/add-barcodes",
                body=json.dumps({"shop_id": "test-shop", "items": []}),
            )
        )

        try:
            response = handle_add_barcodes(context, context)
            print(f"✓ Decorator works! Status: {response._status}")
            assert "Access-Control-Allow-Origin" in response._headers
            print("✓ CORS headers present")
        except AttributeError as e:
            print(f"✗ FAILED: {e}")
            raise

        print("\n✅ All decorator tests passed!")
