from unittest import TestCase
from uuid import UUID

from pydantic_core._pydantic_core import ValidationError  # noqa

from src.schemas.common import ItemBarcodeStatus
from src.schemas.purchased_item import PurchasedItem
from src.tests import SHOP_ITEM_ID_1


class TestPurchasedItem(TestCase):
    def test_init(self):
        self.purchased_item = PurchasedItem(
            name="Test Item",
            quantity=1.0,
            price=10.0,
            item_id=UUID(SHOP_ITEM_ID_1),
        )
        self.assertEqual(self.purchased_item.name, "Test Item")
        self.assertEqual(self.purchased_item.quantity, 1.0)
        self.assertEqual(self.purchased_item.price, 10.0)
        self.assertEqual(self.purchased_item.item_id, UUID(SHOP_ITEM_ID_1))
        self.assertEqual(self.purchased_item.status, ItemBarcodeStatus.PENDING)

    def test_wrong_types(self):
        with self.assertRaises(ValidationError) as ctx:
            PurchasedItem(
                name="Test Item",
                quantity=1.0,
                price=10.0,
                item_id="item_id",
            )
        errors = ctx.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["loc"], ("item_id",))
        self.assertEqual(errors[0]["msg"], "Input should be an instance of UUID")
