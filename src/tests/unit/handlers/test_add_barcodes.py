from unittest import TestCase
from unittest.mock import patch, MagicMock

from src.handlers.add_barcodes import add_barcodes_handler
from src.schemas.common import ItemBarcodeStatus
from src.tests import SHOP_ID_1, BARCODE_1, SHOP_ITEM_ID_1

SUCCESS_RESPONSE_BODY = {"msg": "Purchases successfully added. You can add another URL"}


class TestAddBarcodesHandler(TestCase):
    def setUp(self):
        self.name = "Test Item"
        self.items = [
            {
                "_id": SHOP_ITEM_ID_1,
                "purchase_id": self.name + "_1",
                "status": ItemBarcodeStatus.PENDING.value,
                "barcode": BARCODE_1,
            }
        ]
        self.logger = MagicMock()

    @patch("src.handlers.add_barcodes.init_db_session")
    def test_valid_items(self, mock_init_db_session):
        mock_session = MagicMock()
        mock_init_db_session.return_value = mock_session

        status, body = add_barcodes_handler(SHOP_ID_1, self.items, self.logger)

        self.assertEqual(status, 200)
        self.assertEqual(body, SUCCESS_RESPONSE_BODY)
        mock_session.create_or_update_one.assert_called()

    @patch("src.handlers.add_barcodes.init_db_session")
    def test_invalid_items(self, mock_init_db_session):
        mock_session = MagicMock()
        mock_init_db_session.return_value = mock_session

        invalid_item = {
            "_id": SHOP_ITEM_ID_1,
            "name": self.name,
            "purchase_id": self.name + "_1",
            "status": "INVALID_STATUS",
            "barcode": BARCODE_1,
        }
        items = self.items + [invalid_item]

        status, body = add_barcodes_handler(SHOP_ID_1, items, self.logger)

        self.assertEqual(status, 400)
        self.assertEqual(body["msg"], "Failed to add some items")
        self.assertEqual(
            body["invalid_items"],
            [
                {
                    "error": "'INVALID_STATUS' is not a valid ItemBarcodeStatus",
                    "name": self.name,
                }
            ],
        )
        self.logger.error.assert_called()
