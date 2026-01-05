#!/usr/bin/env python
"""
Local Function Runner for Appwrite Functions

This script allows you to test Appwrite functions locally without
the full Open Runtime executor setup.

Usage:
    python local_appwrite_functions.py <function_name> [--method POST] [--body '{"key": "value"}']

Example:
    python local_appwrite_functions.py parse_from_url --body '{"url": "https://example.com", "user_id": "123"}'
"""

import argparse
import importlib.util
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any


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


class MockContext:
    def __init__(self, req: MockRequest):
        self.req = req
        self.res = MockResponse()
        self._logs = []
        self._errors = []

    def log(self, message: str):
        print(f"[LOG] {message}")
        self._logs.append(message)

    def error(self, message: str):
        print(f"[ERROR] {message}", file=sys.stderr)
        self._errors.append(message)


def load_function(function_name: str):
    """Load a function module from appwrite_functions directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    function_path = os.path.join(script_dir, "appwrite_functions", function_name, "main.py")

    if not os.path.exists(function_path):
        raise FileNotFoundError(f"Function not found: {function_path}")

    spec = importlib.util.spec_from_file_location("main", function_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["main"] = module
    spec.loader.exec_module(module)

    return module


def run_function(function_name: str, method: str = "POST", body: Any = None):
    """Run a function with mock context."""
    # Set up environment for local development
    os.environ.setdefault("ENV_NAME", "dev")
    os.environ.setdefault("DEV_POSTGRES_HOST", "localhost")
    os.environ.setdefault("DEV_POSTGRES_PORT", "5432")
    os.environ.setdefault("DEV_POSTGRES_DB", "receipt_local")
    os.environ.setdefault("DEV_POSTGRES_USER", "postgres")
    os.environ.setdefault("DEV_POSTGRES_PASSWORD", "postgres")

    # Load and run function
    module = load_function(function_name)

    req = MockRequest(method=method, body=body)
    context = MockContext(req)

    print(f"\n{'='*60}")
    print(f"Running function: {function_name}")
    print(f"Method: {method}")
    print(f"Body: {json.dumps(body, indent=2) if body else 'None'}")
    print(f"{'='*60}\n")

    result = module.main(context)

    print(f"\n{'='*60}")
    print(f"Response Status: {context.res._status}")
    print(f"Response Body:")
    print(context.res._body)
    print(f"{'='*60}\n")

    return context.res


def main():
    parser = argparse.ArgumentParser(description="Run Appwrite functions locally")
    parser.add_argument("function", help="Function name (directory name in appwrite_functions)")
    parser.add_argument("--method", "-m", default="POST", help="HTTP method (default: POST)")
    parser.add_argument("--body", "-b", help="Request body as JSON string")
    parser.add_argument("--file", "-f", help="Read request body from JSON file")

    args = parser.parse_args()

    body = None
    if args.body:
        body = json.loads(args.body)
    elif args.file:
        with open(args.file, "r") as f:
            body = json.load(f)

    try:
        run_function(args.function, args.method, body)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error running function: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

