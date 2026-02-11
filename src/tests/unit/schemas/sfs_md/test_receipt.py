from datetime import datetime
from unittest import TestCase
from uuid import UUID

from pydantic_core._pydantic_core import ValidationError  # noqa

from src.schemas.common import CountryCode, CurrencyCode
from src.schemas.purchased_item import PurchasedItem
from src.schemas.sfs_md.receipt import SfsMdReceipt
from src.tests import USER_ID_1


class TestSfsMdReceipt(TestCase):
    def setUp(self):
        self.date = datetime.now()
        self.user_id = UUID(USER_ID_1)
        self.key = 123
        self.total_amount = 100.0
        self.purchases = [PurchasedItem(name="item", price=10.0, quantity=1)]

    def test_auto_generated_fields(self):
        receipt = SfsMdReceipt(
            id="_id",
            date=self.date,
            user_id=self.user_id,
            company_id="company_id",
            company_name="company_name",
            shop_address="shop_address",
            cash_register_id="cash_register_id",
            key=self.key,
            total_amount=self.total_amount,
            purchases=self.purchases,
            receipt_url="http://example.com",
            receipt_canonical_url="wrong_url",
        )
        self.assertTrue(receipt.id.startswith(CountryCode.MOLDOVA))
        self.assertEqual(receipt.country_code, CountryCode.MOLDOVA)
        self.assertEqual(receipt.currency_code, CurrencyCode.MOLDOVAN_LEU)
        self.assertTrue(receipt.receipt_canonical_url.startswith("https://mev.sfs.md"))

    def test_wrong_types(self):
        with self.assertRaises(ValidationError) as ctx:
            SfsMdReceipt(
                id=None,
                date=self.date,
                user_id="NOT_UUID",
                company_id="company_id",
                company_name="company_name",
                shop_address="shop_address",
                cash_register_id="cash_register_id",
                key=self.key,
                total_amount=self.total_amount,
                purchases=self.purchases,
                receipt_url="http://example.com",
                shop_id="NOT_UUID",
            )

        errors = ctx.exception.errors()
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]["loc"], ("user_id",))
        self.assertEqual(errors[0]["msg"], "Input should be an instance of UUID")
        self.assertEqual(errors[1]["loc"], ("shop_id",))
        self.assertEqual(errors[1]["msg"], "Input should be an instance of UUID")
