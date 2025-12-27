from unittest import TestCase
from unittest.mock import MagicMock
from uuid import UUID

from azure.functions import HttpRequest, HttpResponse

from src.helpers.azure_function import (
    get_form_data,
    get_cookies,
    format_cookie,
    format_session_cookie,
    format_user_id_cookie,
    format_invalid_user_id_cookie,
    build_response,
)
from src.schemas.user_identity import IdentityProvider
from src.schemas.user_session import UserSessionCookie
from src.tests import SESSION_ID, USER_ID_1


class TestAzureFunction(TestCase):
    def setUp(self):
        self.req = MagicMock(spec=HttpRequest)

    def test_get_form_data(self):
        self.req.form = {"key1": " value1 ", "key2": " value2 "}
        result = get_form_data(self.req, "key1", "key2")
        self.assertEqual(result, ("value1", "value2"))

    def test_get_cookies(self):
        self.req.headers = {
            "Cookie": f"session_key=google_{SESSION_ID}; user_id={USER_ID_1}"
        }
        result = get_cookies(self.req.headers, MagicMock())
        expected = UserSessionCookie(
            session_id=UUID(SESSION_ID),
            identity_provider=IdentityProvider.GOOGLE,
            user_id=UUID(USER_ID_1),
        )
        self.assertEqual(result, expected)

    def test_format_cookie(self):
        result = format_cookie("key", "value")
        self.assertTrue(result.startswith("key=value;"))

    def test_format_session_cookie(self):
        cookie = UserSessionCookie(
            session_id=UUID(SESSION_ID),
            identity_provider=IdentityProvider.GOOGLE,
            user_id=None,
        )
        result = format_session_cookie(cookie)
        self.assertTrue(result.startswith(f"session_key=google_{SESSION_ID};"))

    def test_format_user_id_cookie(self):
        result = format_user_id_cookie(UUID(USER_ID_1))
        self.assertTrue(result.startswith(f"user_id={USER_ID_1};"))

    def test_format_invalid_user_id_cookie(self):
        result = format_invalid_user_id_cookie()
        self.assertTrue(result.startswith("user_id=;"))

    def test_build_response_from_str_body(self):
        response = build_response(200, "test body", "text/plain")
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_body(), "test body".encode("utf-8"))
        self.assertEqual(response.mimetype, "text/plain")
        self.assertEqual(dict(response.headers), {"access-control-allow-origin": "*"})

    def test_build_response_from_dict_body(self):
        response = build_response(200, {"key": "value"}, "application/json")
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_body(), '{"key": "value"}'.encode("utf-8"))
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(dict(response.headers), {"access-control-allow-origin": "*"})
