from unittest import TestCase
from uuid import UUID

from src.schemas.common import ItemBarcodeStatus
from src.schemas.shop_item import ShopItem
from src.tests import BARCODE_1, SHOP_ID_1


class TestShopItem(TestCase):
    def setUp(self):
        self.name = "Test Item"
        self.status = ItemBarcodeStatus.ADDED

    def test_auto_generated_fields(self):
        item = ShopItem(
            shop_id=SHOP_ID_1, name=self.name, status=self.status, barcode=BARCODE_1
        )
        self.assertIsInstance(item, ShopItem)
        self.assertIsInstance(item.id, UUID)

    def test_shop_id_not_int(self):
        with self.assertRaises(ValueError):
            ShopItem(
                shop_id="NOT_INT", name=self.name, status=self.status, barcode=BARCODE_1
            )

    def test_status_not_valid(self):
        with self.assertRaises(ValueError):
            ShopItem(
                shop_id=SHOP_ID_1,
                name=self.name,
                status="INVALID_STATUS",
                barcode=BARCODE_1,
            )

    def test_barcode_not_provided(self):
        with self.assertRaises(ValueError):
            ShopItem(shop_id=SHOP_ID_1, name=self.name, status=self.status, barcode=None)

    def test_barcode_not_digit(self):
        with self.assertRaises(ValueError):
            ShopItem(
                shop_id=SHOP_ID_1, name=self.name, status=self.status, barcode="not_digit"
            )

    def test_barcode_not_valid(self):
        with self.assertRaises(ValueError):
            ShopItem(
                shop_id=SHOP_ID_1,
                name=self.name,
                status=self.status,
                barcode="1111111111",
            )

    def test_id_not_uuid(self):
        with self.assertRaises(ValueError):
            ShopItem(
                id="not_uuid",
                shop_id=SHOP_ID_1,
                name=self.name,
                status=self.status,
                barcode=BARCODE_1,
            )
