from unittest import TestCase
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import UUID

import pytest

from src.handlers.parse_from_url import parse_from_url_handler
from src.tests import USER_ID_1


class TestParseFromUrlHandlerSync(TestCase):
    """Synchronous test setup - for non-async parts"""

    def setUp(self):
        self.url = "http://valid.url"
        self.user_id = USER_ID_1
        self.logger = MagicMock()
        self.db_api = AsyncMock()


@pytest.mark.asyncio
class TestParseFromUrlHandler:
    """Async tests for parse_from_url_handler"""

    def setup_method(self):
        """Setup for each test method"""
        self.url = "http://valid.url"
        self.user_id = USER_ID_1
        self.logger = MagicMock()
        self.db_api = AsyncMock()

    async def test_no_url(self):
        result = await parse_from_url_handler("", self.user_id, self.logger, self.db_api)
        assert result.status_code == 400
        assert result.detail == "Unsupported URL"

    async def test_invalid_user_id(self):
        # UUID validation happens in the handler, need to check actual behavior
        result = await parse_from_url_handler(
            self.url, "invalid_user_id", self.logger, self.db_api
        )
        assert result.status_code == 400

    @patch("src.handlers.parse_from_url.SfsMdReceiptParser")
    async def test_unsupported_url(self, mock_parser):
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.validate_receipt_url.return_value = False
        result = await parse_from_url_handler(
            self.url, self.user_id, self.logger, self.db_api
        )
        assert result.status_code == 400
        assert result.detail == "Unsupported URL"

    @patch("src.handlers.parse_from_url.SfsMdReceiptParser")
    async def test_failed_to_fetch_receipt(self, mock_parser):
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.validate_receipt_url.return_value = True
        mock_parser_instance.get_receipt = AsyncMock(return_value=None)
        result = await parse_from_url_handler(
            self.url, UUID(self.user_id), self.logger, self.db_api
        )
        assert result.status_code == 400
        assert result.detail == "Failed to fetch receipt"

    @patch("src.handlers.parse_from_url.SfsMdReceiptParser")
    @patch("src.handlers.parse_from_url.get_html")
    async def test_receipt_successfully_processed(self, mock_get_html, mock_parser):
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.validate_receipt_url.return_value = True
        mock_parser_instance.get_receipt = AsyncMock(return_value=None)
        mock_get_html.return_value = "<html></html>"
        mock_receipt = MagicMock()
        mock_receipt.model_dump.return_value = {"id": "receipt_id"}
        mock_receipt.persist = AsyncMock(return_value=mock_receipt)
        # pylint: disable=line-too-long
        mock_parser_instance.parse_html.return_value.build_receipt.return_value = (
            mock_receipt
        )
        result = await parse_from_url_handler(
            self.url, UUID(self.user_id), self.logger, self.db_api
        )
        assert result.status_code == 200
        assert result.detail == "Receipt successfully processed"
        assert result.data == {"id": "receipt_id"}

    @patch("src.handlers.parse_from_url.SfsMdReceiptParser")
    async def test_receipt_retrieval_error(self, mock_parser):
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.validate_receipt_url.return_value = True
        mock_parser_instance.get_receipt = AsyncMock(side_effect=Exception("DB Error"))

        result = await parse_from_url_handler(
            self.url, UUID(self.user_id), self.logger, self.db_api
        )
        assert result.status_code == 500
        assert result.detail == "Error retrieving receipt"

    @patch("src.handlers.parse_from_url.SfsMdReceiptParser")
    async def test_receipt_found_directly(self, mock_parser):
        mock_parser_instance = mock_parser.return_value
        mock_parser_instance.validate_receipt_url.return_value = True

        mock_receipt = MagicMock()
        mock_receipt.model_dump.return_value = {"_id": "receipt_id_direct"}
        mock_parser_instance.get_receipt = AsyncMock(return_value=mock_receipt)

        result = await parse_from_url_handler(
            self.url, UUID(self.user_id), self.logger, self.db_api
        )
        assert result.status_code == 200
        assert result.detail == "Receipt successfully processed"
        assert result.data == {"_id": "receipt_id_direct"}
