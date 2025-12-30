from unittest import TestCase
from unittest.mock import patch, MagicMock

from src.handlers.parse_from_url import parse_from_url_handler
from src.tests import USER_ID_1


class TestParseFromUrlHandler(TestCase):
    def setUp(self):
        self.url = "http://valid.url"
        self.user_id = USER_ID_1
        self.logger = MagicMock()

    def test_no_url(self):
        status, body = parse_from_url_handler("", self.user_id, self.logger)
        self.assertEqual(status, 400)
        self.assertEqual(body, {"msg": "URL is required"})

    def test_invalid_user_id(self):
        status, body = parse_from_url_handler(self.url, "invalid_user_id", self.logger)
        self.assertEqual(status, 400)
        self.assertEqual(body, {"msg": "Invalid user ID"})

    @patch("src.handlers.parse_from_url.SfsMdReceiptParser")
    def test_unsupported_url(self, mock_parser):
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.validate_receipt_url.return_value = False
        status, body = parse_from_url_handler(self.url, self.user_id, self.logger)
        self.assertEqual(status, 400)
        self.assertEqual(body, {"msg": "Unsupported URL"})

    @patch("src.handlers.parse_from_url.SfsMdReceiptParser")
    @patch("src.handlers.parse_from_url.get_html")
    def test_failed_to_fetch_receipt(self, mock_get_html, mock_parser):
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.validate_receipt_url.return_value = True
        mock_parser_instance.get_receipt.return_value = None
        mock_get_html.return_value = None
        status, body = parse_from_url_handler(self.url, self.user_id, self.logger)
        self.assertEqual(status, 400)
        self.assertEqual(body, {"msg": "Failed to fetch receipt"})

    @patch("src.handlers.parse_from_url.SfsMdReceiptParser")
    @patch("src.handlers.parse_from_url.get_html")
    def test_receipt_successfully_processed(self, mock_get_html, mock_parser):
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.validate_receipt_url.return_value = True
        mock_parser_instance.get_receipt.return_value = None
        mock_get_html.return_value = "<html></html>"
        mock_receipt = MagicMock()
        mock_receipt.model_dump.return_value = {"id": "receipt_id"}
        # pylint: disable=line-too-long
        mock_parser_instance.parse_html.return_value.build_receipt.return_value.persist.return_value = (
            mock_receipt
        )
        status, body = parse_from_url_handler(self.url, self.user_id, self.logger)
        self.assertEqual(status, 200)
        self.assertEqual(
            body, {"msg": "Receipt successfully processed", "data": {"id": "receipt_id"}}
        )

    @patch("src.handlers.parse_from_url.SfsMdReceiptParser")
    def test_receipt_retrieval_error(self, mock_parser):
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.validate_receipt_url.return_value = True
        mock_parser_instance.get_receipt.side_effect = Exception("DB Error")

        status, body = parse_from_url_handler(self.url, self.user_id, self.logger)
        self.assertEqual(status, 500)
        self.assertEqual(body, {"msg": "Error retrieving receipt"})

    @patch("src.handlers.parse_from_url.SfsMdReceiptParser")
    def test_receipt_found_directly(self, mock_parser):
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.validate_receipt_url.return_value = True

        mock_receipt = MagicMock()
        mock_receipt.model_dump.return_value = {"id": "receipt_id_direct"}
        mock_parser_instance.get_receipt.return_value = mock_receipt

        status, body = parse_from_url_handler(self.url, self.user_id, self.logger)
        self.assertEqual(status, 200)
        self.assertEqual(
            body,
            {"msg": "Receipt successfully processed", "data": {"id": "receipt_id_direct"}},
        )

