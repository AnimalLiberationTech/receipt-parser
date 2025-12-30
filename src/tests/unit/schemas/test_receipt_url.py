from unittest import TestCase
from src.schemas.receipt_url import ReceiptUrl
from src.schemas.common import CountryCode

class TestReceiptUrl(TestCase):
    def test_create_without_id(self):
        url = "https://mev.sfs.md/receipt-verifier/123"
        receipt_url = ReceiptUrl(
            url=url,
            receipt_id="receipt_123",
            country_code=CountryCode.MOLDOVA
        )
        self.assertIsNotNone(receipt_url.id)
        self.assertEqual(receipt_url.url, url)

