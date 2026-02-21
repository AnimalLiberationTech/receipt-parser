from datetime import datetime
from http import HTTPStatus
from unittest import TestCase
from unittest.mock import patch, MagicMock

from src.handlers.link_shop import link_shop_handler
from src.schemas.common import OsmType, CountryCode, CurrencyCode
from src.tests import USER_ID_1, SHOP_ID_1


class TestLinkShopHandler(TestCase):
    def setUp(self):
        self.logger = MagicMock()
        self.receipt_id = "receipt-uuid"

    @patch("src.handlers.link_shop.lookup_osm_data")
    def test_osm_lookup_fails(self, mock_lookup_osm_data):
        """Test when OSM lookup returns no data."""
        mock_lookup_osm_data.return_value = None
        mock_db_api = MagicMock()

        response = link_shop_handler(
            OsmType.NODE, 123, self.receipt_id, self.logger, mock_db_api
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.detail, "Failed to get OSM shop details")

    @patch("src.handlers.link_shop.lookup_osm_data")
    def test_receipt_lookup_fails(self, mock_lookup_osm_data):
        """Test when receipt lookup via db_api fails."""
        mock_lookup_osm_data.return_value = {
            "lat": "10.2",
            "lon": "20.1",
            "display_name": "shop_name",
            "address": {"city": "Chisinau", "country": "Moldova"},
        }

        # db_api call returns error response
        mock_db_api = MagicMock(
            return_value={
                "status_code": HTTPStatus.NOT_FOUND,
                "detail": "Receipt not found",
            }
        )

        response = link_shop_handler(
            OsmType.NODE, 123, self.receipt_id, self.logger, mock_db_api
        )

        # Verify receipt was queried
        mock_db_api.assert_called_once()
        call_args = mock_db_api.call_args
        self.assertEqual(call_args[0][0], "/receipt/get-by-id")
        self.assertEqual(call_args[0][1], "GET")

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.detail, "Failed to get the receipt")

    @patch("src.handlers.link_shop.lookup_osm_data")
    def test_shop_creation_fails(self, mock_lookup_osm_data):
        """Test when shop get-or-create fails."""
        osm_data = {
            "lat": "10.2",
            "lon": "20.1",
            "display_name": "shop_name",
            "address": {"city": "Chisinau", "country": "Moldova"},
        }
        mock_lookup_osm_data.return_value = osm_data

        receipt_data = {
            "status_code": HTTPStatus.OK,
            "data": {
                "id": self.receipt_id,
                "user_id": USER_ID_1,
                "country_code": CountryCode.MOLDOVA,
                "company_id": "company-123",
                "shop_address": "Some street 123",
            },
        }

        # db_api: first call gets receipt, second call fails to create shop
        mock_db_api = MagicMock(
            side_effect=[
                receipt_data,
                {"status_code": HTTPStatus.INTERNAL_SERVER_ERROR, "detail": "DB error"},
            ]
        )

        response = link_shop_handler(
            OsmType.WAY, 456, self.receipt_id, self.logger, mock_db_api
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.detail, "Failed to get or create shop")

    @patch("src.handlers.link_shop.lookup_osm_data")
    def test_add_shop_id_to_receipt_fails(self, mock_lookup_osm_data):
        """Test when adding shop_id to receipt fails."""
        osm_data = {
            "lat": "10.2",
            "lon": "20.1",
            "display_name": "shop_name",
            "address": {"city": "Chisinau", "country": "Moldova"},
        }
        mock_lookup_osm_data.return_value = osm_data

        receipt_data = {
            "status_code": HTTPStatus.OK,
            "data": {
                "id": self.receipt_id,
                "user_id": USER_ID_1,
                "country_code": CountryCode.MOLDOVA,
                "company_id": "company-123",
                "company_name": "Shop Company",
                "shop_address": "Some street 123",
                "date": datetime(2026, 2, 21),
                "cash_register_id": "register-1",
                "key": 12345,
                "currency_code": CurrencyCode.MOLDOVAN_LEU,
                "total_amount": 100.0,
                "purchases": [],
                "receipt_url": "https://example.com/receipt",
            },
        }

        shop_data = {
            "status_code": HTTPStatus.OK,
            "data": {
                "id": SHOP_ID_1,
                "country_code": CountryCode.MOLDOVA,
                "company_id": "company-123",
                "address": "Some street 123",
            },
        }

        # db_api: get receipt OK, create shop OK, add shop_id FAILS
        mock_db_api = MagicMock(
            side_effect=[
                receipt_data,
                shop_data,
                {"status_code": HTTPStatus.INTERNAL_SERVER_ERROR, "detail": "DB error"},
            ]
        )

        response = link_shop_handler(
            OsmType.RELATION, 789, self.receipt_id, self.logger, mock_db_api
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.detail, "Failed to add shop id to receipt")

    @patch("src.handlers.link_shop.lookup_osm_data")
    def test_shop_successfully_linked(self, mock_lookup_osm_data):
        """Test successful shop linking flow."""
        osm_data = {
            "lat": "10.2",
            "lon": "20.1",
            "display_name": "shop_name",
            "address": {"city": "Chisinau", "country": "Moldova"},
        }
        mock_lookup_osm_data.return_value = osm_data

        receipt_data = {
            "status_code": HTTPStatus.OK,
            "data": {
                "id": self.receipt_id,
                "user_id": USER_ID_1,
                "country_code": CountryCode.MOLDOVA,
                "company_id": "company-123",
                "company_name": "Shop Company",
                "shop_address": "Some street 123",
                "date": datetime(2026, 2, 21),
                "cash_register_id": "register-1",
                "key": 12345,
                "currency_code": CurrencyCode.MOLDOVAN_LEU,
                "total_amount": 100.0,
                "purchases": [],
                "receipt_url": "https://example.com/receipt",
            },
        }

        shop_data = {
            "status_code": HTTPStatus.OK,
            "data": {
                "id": SHOP_ID_1,
                "country_code": CountryCode.MOLDOVA,
                "company_id": "company-123",
                "address": "Some street 123",
            },
        }

        add_shop_data = {
            "status_code": HTTPStatus.OK,
            "data": {"success": True},
        }

        # All db_api calls succeed
        mock_db_api = MagicMock(
            side_effect=[
                receipt_data,
                shop_data,
                add_shop_data,
            ]
        )

        response = link_shop_handler(
            OsmType.NODE, 123, self.receipt_id, self.logger, mock_db_api
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.detail, "Shop successfully linked")
        self.assertEqual(response.data["shop_id"], SHOP_ID_1)

        # Verify all three db_api calls were made in the correct order
        self.assertEqual(mock_db_api.call_count, 3)

        # First call: get receipt
        first_call = mock_db_api.call_args_list[0]
        self.assertEqual(first_call[0][0], "/receipt/get-by-id")
        self.assertEqual(first_call[0][1], "GET")

        # Second call: get or create shop
        second_call = mock_db_api.call_args_list[1]
        self.assertEqual(second_call[0][0], "/shop/get-or-create")
        self.assertEqual(second_call[0][1], "POST")

        # Third call: add shop id to receipt
        third_call = mock_db_api.call_args_list[2]
        self.assertEqual(third_call[0][0], "/receipt/add-shop-id")
        self.assertEqual(third_call[0][1], "POST")
