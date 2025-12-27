from unittest import TestCase
from unittest.mock import patch, MagicMock
from uuid import UUID

from src.handlers.link_shop import link_shop_handler
from src.helpers.osm import OSM_HOST
from src.schemas.common import OsmType, CountryCode
from src.tests import USER_ID_1, SHOP_ID_1


class TestLinkShopHandler(TestCase):
    def setUp(self):
        self.logger = MagicMock()

    def test_invalid_url(self):
        status, body = link_shop_handler(
            "invalid_url", USER_ID_1, "receipt_id", self.logger
        )
        self.assertEqual(status, 400)
        self.assertEqual(body, {"msg": "Unsupported URL"})

    @patch("src.handlers.link_shop.init_db_session")
    def test_receipt_not_found(self, mock_init_db_session):
        mock_session = MagicMock()
        mock_init_db_session.return_value = mock_session
        mock_session.read_one.return_value = None

        status, body = link_shop_handler(OSM_HOST, USER_ID_1, "receipt_id", self.logger)

        self.assertEqual(status, 404)
        self.assertEqual(body, {"msg": "Receipt not found"})

    @patch("src.handlers.link_shop.init_db_session")
    def test_invalid_osm_url(self, mock_init_db_session):
        mock_session = MagicMock()
        mock_init_db_session.return_value = mock_session
        mock_session.read_many.return_value = []

        status, body = link_shop_handler(OSM_HOST, USER_ID_1, "receipt_id", self.logger)

        self.assertEqual(status, 400)
        self.assertEqual(body, {"msg": "Invalid OSM URL"})

    @patch("src.handlers.link_shop.init_db_session")
    @patch("src.handlers.link_shop.parse_osm_url")
    @patch("src.handlers.link_shop.lookup_osm_object")
    def test_failed_to_get_osm_shop_details(
        self, mock_lookup_osm_object, mock_parse_osm_url, mock_init_db_session
    ):
        mock_session = MagicMock()
        mock_init_db_session.return_value = mock_session
        mock_session.read_many.return_value = []

        mock_parse_osm_url.return_value = ("osm_type", "osm_key")
        mock_lookup_osm_object.return_value = None

        status, body = link_shop_handler(
            f"{OSM_HOST}/node/123", USER_ID_1, "receipt_id", self.logger
        )

        self.assertEqual(status, 400)
        self.assertEqual(body, {"msg": "Failed to get OSM shop details"})

    @patch("src.handlers.link_shop.init_db_session")
    def test_existing_shop_successfully_linked(self, mock_init_db_session):
        shop_data = {"id": SHOP_ID_1}
        mock_session = MagicMock()
        mock_init_db_session.return_value = mock_session
        mock_session.read_many.return_value = [shop_data]
        mock_session.update_one.return_value = True

        status, body = link_shop_handler(
            f"{OSM_HOST}/node/123", USER_ID_1, "receipt_id", self.logger
        )

        self.assertEqual(status, 200)
        self.assertEqual(body["msg"], "Shop successfully linked")
        self.assertEqual(body["data"], {"shop_id": SHOP_ID_1})

    @patch("src.handlers.link_shop.init_db_session")
    @patch("src.handlers.link_shop.parse_osm_url")
    @patch("src.handlers.link_shop.lookup_osm_object")
    def test_new_shop_successfully_linked(
        self, mock_lookup_osm_object, mock_parse_osm_url, mock_init_db_session
    ):
        mock_session = MagicMock()
        mock_init_db_session.return_value = mock_session
        mock_session.read_one.return_value = {
            "country_code": CountryCode.MOLDOVA,
            "company_id": "company_id",
            "shop_address": "shop_address",
        }
        mock_session.read_many.return_value = []  # shop doesn't exist
        mock_session.create_one.return_value = True
        mock_session.update_one.return_value = True
        mock_parse_osm_url.return_value = (OsmType.WAY, "123")
        mock_lookup_osm_object.return_value = {
            "lat": "10.2",
            "lon": "20.1",
            "display_name": "display_name",
            "address": {"city": "city", "country": "country"},
        }

        status, body = link_shop_handler(
            f"{OSM_HOST}/node/123", USER_ID_1, "receipt_id", self.logger
        )

        self.assertEqual(status, 200)
        self.assertTrue(UUID(body["data"]["shop_id"]))  # assert it's a valid UUID
