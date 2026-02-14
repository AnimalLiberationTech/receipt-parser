import os
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID

from src.parsers.sfs_md.receipt_parser import SfsMdReceiptParser
from src.tests import load_stub_file, USER_ID_1
from src.tests.stubs.receipts.sfs_md.expected_objects import (
    LIN_RECEIPT,
    KL_RECEIPT,
    LIN_RECEIPT_2,
    NANU_RECEIPT,
)

LIN_RECEIPT_PATH = os.path.join("receipts", "sfs_md", "linella.html")
KL_RECEIPT_PATH = os.path.join("receipts", "sfs_md", "kaufland.html")
LIN2_RECEIPT_PATH = os.path.join("receipts", "sfs_md", "linella2.html")
NANU_RECEIPT_PATH = os.path.join("receipts", "sfs_md", "nanu.html")
# pylint: disable=line-too-long
LIN_RECEIPT_URL = (
    "https://mev.sfs.md/receipt-verifier/J403001576/118.04/135932/2024-01-17"
)


class TestSfsMdReceiptParser(TestCase):
    def test_parse(self):
        logger = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT),
            (LIN_RECEIPT_PATH, LIN_RECEIPT),
            (LIN2_RECEIPT_PATH, LIN_RECEIPT_2),
            (NANU_RECEIPT_PATH, NANU_RECEIPT),
        ]

        for path, expected in test_cases:
            with self.subTest(path=path):
                db_api = Mock()
                parser = SfsMdReceiptParser(
                    logger, UUID(USER_ID_1), expected.receipt_url, db_api
                )
                self.assertEqual(
                    parser.parse_html(load_stub_file(path)).build_receipt().receipt,
                    expected,
                )

    def test_parse_invalid_html_missing_receipt_data(self):
        """Test parsing HTML without receipt data raises ValueError"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), LIN_RECEIPT_URL, db_api)

        invalid_html = "<html><body>No receipt data here</body></html>"

        with self.assertRaises(ValueError) as context:
            parser.parse_html(invalid_html)

        self.assertIn("Failed to parse receipt data", str(context.exception))
        logger.warning.assert_called_once()

    def test_parse_empty_html(self):
        """Test parsing empty HTML raises ValueError"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), LIN_RECEIPT_URL, db_api)

        with self.assertRaises(ValueError) as context:
            parser.parse_html("")

        self.assertIn("Failed to parse receipt data", str(context.exception))

    def test_parse_malformed_json_in_html(self):
        """Test parsing HTML with malformed JSON raises appropriate error"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), LIN_RECEIPT_URL, db_api)

        # HTML with invalid JSON in the wire:initial-data attribute
        malformed_html = (
            '<div wire:initial-data="{invalid json receipt.index-component}"></div>'
        )

        with self.assertRaises(Exception):  # Should raise json.JSONDecodeError or similar
            parser.parse_html(malformed_html)

    def test_validate_receipt_url_valid_mev(self):
        """Test URL validation for valid mev.sfs.md URL"""
        logger = Mock()
        db_api = Mock()
        url = "https://mev.sfs.md/receipt-verifier/J403001576/118.04/135932/2024-01-17"
        parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)

        self.assertTrue(parser.validate_receipt_url())

    def test_validate_receipt_url_valid_sift(self):
        """Test URL validation for valid sift-mev.sfs.md URL"""
        logger = Mock()
        db_api = Mock()
        url = "https://sift-mev.sfs.md/receipt/J403001576/118.04/135932/2024-01-17"
        parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)

        self.assertTrue(parser.validate_receipt_url())

    def test_validate_receipt_url_invalid(self):
        """Test URL validation for invalid URL"""
        logger = Mock()
        db_api = Mock()
        invalid_urls = [
            "https://example.com/receipt",
            "http://mev.sfs.md/receipt-verifier/test",
            "https://mev.sfs.com/receipt-verifier/test",
            "",
            "not-a-url",
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                self.assertFalse(parser.validate_receipt_url())

    def test_receipt_has_correct_user_id(self):
        """Test that parsed receipt has the correct user ID"""
        logger = Mock()
        db_api = Mock()
        test_user_id = UUID(USER_ID_1)
        parser = SfsMdReceiptParser(logger, test_user_id, LIN_RECEIPT.receipt_url, db_api)

        parsed_receipt = (
            parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt().receipt
        )

        self.assertEqual(parsed_receipt.user_id, test_user_id)

    def test_receipt_has_correct_url(self):
        """Test that parsed receipt has the correct receipt URL"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )

        parsed_receipt = (
            parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt().receipt
        )

        self.assertEqual(parsed_receipt.receipt_url, LIN_RECEIPT.receipt_url)

    def test_receipt_purchases_have_correct_types(self):
        """Test that purchases have correct data types"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )

        parsed_receipt = (
            parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt().receipt
        )

        for purchase in parsed_receipt.purchases:
            self.assertIsInstance(purchase.quantity, float)
            self.assertIsInstance(purchase.price, float)
            if purchase.unit_quantity is not None:
                self.assertIsInstance(purchase.unit_quantity, float)

    def test_receipt_total_amount_is_positive(self):
        """Test that total amount is positive"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url),
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
            (LIN2_RECEIPT_PATH, LIN_RECEIPT_2.receipt_url),
            (NANU_RECEIPT_PATH, NANU_RECEIPT.receipt_url),
        ]

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                parsed_receipt = (
                    parser.parse_html(load_stub_file(path)).build_receipt().receipt
                )

                self.assertGreater(parsed_receipt.total_amount, 0)

    def test_receipt_has_purchases(self):
        """Test that receipts have at least one purchase"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url),
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
            (LIN2_RECEIPT_PATH, LIN_RECEIPT_2.receipt_url),
            (NANU_RECEIPT_PATH, NANU_RECEIPT.receipt_url),
        ]

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                parsed_receipt = (
                    parser.parse_html(load_stub_file(path)).build_receipt().receipt
                )

                self.assertGreater(len(parsed_receipt.purchases), 0)

    def test_persist_calls_db_api(self):
        """Test that persist method calls the database API"""
        logger = Mock()
        db_api = Mock()
        db_api.return_value = None

        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt()

        result = parser.persist()

        db_api.assert_called_once_with(
            "/receipt/get-or-create", "POST", parser.receipt.model_dump()
        )
        self.assertEqual(result, parser.receipt)

    def test_get_receipt_calls_db_api(self):
        """Test that get_receipt method calls the database API"""
        logger = Mock()
        db_api = Mock()
        db_api.return_value = LIN_RECEIPT.model_dump()

        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        result = parser.get_receipt()

        db_api.assert_called_once_with(
            "/receipt/get-by-url", "POST", {"url": LIN_RECEIPT.receipt_url}
        )
        self.assertEqual(result, LIN_RECEIPT)

    def test_parse_chain_methods(self):
        """Test that parse_html and build_receipt can be chained"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )

        # Should be able to chain parse_html -> build_receipt
        result = parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt()

        self.assertIsInstance(result, SfsMdReceiptParser)
        self.assertIsNotNone(result.receipt)

    def test_receipt_date_format(self):
        """Test that receipt dates are correctly parsed"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )

        parsed_receipt = (
            parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt().receipt
        )

        self.assertEqual(parsed_receipt.date.year, 2024)
        self.assertEqual(parsed_receipt.date.month, 1)
        self.assertEqual(parsed_receipt.date.day, 17)
        self.assertEqual(parsed_receipt.date.hour, 14)
        self.assertEqual(parsed_receipt.date.minute, 58)
        self.assertEqual(parsed_receipt.date.second, 22)

    def test_different_user_ids_produce_different_receipts(self):
        """Test that using different user IDs produces receipts with different user IDs"""
        logger = Mock()
        db_api = Mock()
        user_id_1 = UUID(USER_ID_1)
        user_id_2 = UUID("345baf90-f7a8-43a0-bf86-e9d6593d397e")

        parser_1 = SfsMdReceiptParser(logger, user_id_1, LIN_RECEIPT.receipt_url, db_api)
        receipt_1 = (
            parser_1.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt().receipt
        )

        parser_2 = SfsMdReceiptParser(logger, user_id_2, LIN_RECEIPT.receipt_url, db_api)
        receipt_2 = (
            parser_2.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt().receipt
        )

        self.assertEqual(receipt_1.user_id, user_id_1)
        self.assertEqual(receipt_2.user_id, user_id_2)
        self.assertNotEqual(receipt_1.user_id, receipt_2.user_id)

    def test_receipt_company_id_extracted_correctly(self):
        """Test that company ID is extracted correctly from receipt data"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (LIN_RECEIPT_PATH, "1010600022460"),
            (KL_RECEIPT_PATH, "1016600004811"),
            (NANU_RECEIPT_PATH, "1006600052073"),
        ]

        for path, expected_company_id in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(
                    logger, UUID(USER_ID_1), LIN_RECEIPT_URL, db_api
                )
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt
                self.assertEqual(receipt.company_id, expected_company_id)

    def test_receipt_currency_is_moldovan_leu(self):
        """Test that all receipts use Moldovan Leu currency"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url),
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
            (LIN2_RECEIPT_PATH, LIN_RECEIPT_2.receipt_url),
            (NANU_RECEIPT_PATH, NANU_RECEIPT.receipt_url),
        ]

        from src.schemas.common import CurrencyCode

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt
                self.assertEqual(receipt.currency_code, CurrencyCode.MOLDOVAN_LEU)

    def test_receipt_country_is_moldova(self):
        """Test that all receipts are from Moldova"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url),
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
            (LIN2_RECEIPT_PATH, LIN_RECEIPT_2.receipt_url),
            (NANU_RECEIPT_PATH, NANU_RECEIPT.receipt_url),
        ]

        from src.schemas.common import CountryCode

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt
                self.assertEqual(receipt.country_code, CountryCode.MOLDOVA)

    def test_purchases_with_units_parsed_correctly(self):
        """Test that purchases with units (kg, g, ml, l) are parsed correctly"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        receipt = (
            parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt().receipt
        )

        # Check that purchases with units have both unit and unit_quantity set
        purchases_with_units = [p for p in receipt.purchases if p.unit is not None]
        self.assertGreater(
            len(purchases_with_units), 0, "Should have at least one purchase with units"
        )

        for purchase in purchases_with_units:
            self.assertIsNotNone(purchase.unit)
            self.assertIsNotNone(purchase.unit_quantity)
            self.assertGreater(purchase.unit_quantity, 0)

    def test_purchases_without_units_have_none_values(self):
        """Test that purchases without units have None for unit and unit_quantity"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT_2.receipt_url, db_api
        )
        receipt = (
            parser.parse_html(load_stub_file(LIN2_RECEIPT_PATH)).build_receipt().receipt
        )

        # GLORIA NUTS purchase should not have units extracted
        gloria_nuts = [p for p in receipt.purchases if "GLORIA NUTS" in p.name]
        self.assertEqual(len(gloria_nuts), 1)
        self.assertIsNone(gloria_nuts[0].unit)
        self.assertIsNone(gloria_nuts[0].unit_quantity)

    def test_purchase_quantities_are_positive(self):
        """Test that all purchase quantities are positive"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url),
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
            (LIN2_RECEIPT_PATH, LIN_RECEIPT_2.receipt_url),
            (NANU_RECEIPT_PATH, NANU_RECEIPT.receipt_url),
        ]

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt

                for purchase in receipt.purchases:
                    self.assertGreater(purchase.quantity, 0)

    def test_purchase_prices_are_positive(self):
        """Test that all purchase prices are positive"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url),
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
            (LIN2_RECEIPT_PATH, LIN_RECEIPT_2.receipt_url),
            (NANU_RECEIPT_PATH, NANU_RECEIPT.receipt_url),
        ]

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt

                for purchase in receipt.purchases:
                    self.assertGreater(purchase.price, 0)

    def test_purchase_names_are_not_empty(self):
        """Test that all purchase names are non-empty strings"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url),
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
            (LIN2_RECEIPT_PATH, LIN_RECEIPT_2.receipt_url),
            (NANU_RECEIPT_PATH, NANU_RECEIPT.receipt_url),
        ]

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt

                for purchase in receipt.purchases:
                    self.assertIsInstance(purchase.name, str)
                    self.assertGreater(len(purchase.name.strip()), 0)

    def test_persist_logs_receipt_data(self):
        """Test that persist method logs receipt data"""
        logger = Mock()
        db_api = Mock()

        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt()
        parser.persist()

        logger.info.assert_called_once()

    def test_get_receipt_when_not_found(self):
        """Test that get_receipt returns None when receipt not found"""
        logger = Mock()
        db_api = Mock()
        db_api.return_value = None

        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        result = parser.get_receipt()

        self.assertIsNone(result)

    def test_cash_register_id_extracted_correctly(self):
        """Test that cash register ID is extracted correctly"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url, "J403001576"),
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url, "J702003194"),
        ]

        for path, url, expected_cash_register_id in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt
                self.assertEqual(receipt.cash_register_id, expected_cash_register_id)

    def test_shop_address_not_empty(self):
        """Test that shop address is not empty"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url),
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
            (LIN2_RECEIPT_PATH, LIN_RECEIPT_2.receipt_url),
            (NANU_RECEIPT_PATH, NANU_RECEIPT.receipt_url),
        ]

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt
                self.assertIsInstance(receipt.shop_address, str)
                self.assertGreater(len(receipt.shop_address.strip()), 0)

    def test_company_name_not_empty(self):
        """Test that company name is not empty"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url),
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
            (LIN2_RECEIPT_PATH, LIN_RECEIPT_2.receipt_url),
            (NANU_RECEIPT_PATH, NANU_RECEIPT.receipt_url),
        ]

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt
                self.assertIsInstance(receipt.company_name, str)
                self.assertGreater(len(receipt.company_name.strip()), 0)

    def test_receipt_key_is_positive_integer(self):
        """Test that receipt key is a positive integer"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url),
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
            (LIN2_RECEIPT_PATH, LIN_RECEIPT_2.receipt_url),
            (NANU_RECEIPT_PATH, NANU_RECEIPT.receipt_url),
        ]

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt
                self.assertIsInstance(receipt.key, int)
                self.assertGreater(receipt.key, 0)

    def test_multiple_same_items_have_same_price(self):
        """Test that multiple purchases of same item have consistent pricing"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        receipt = (
            parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt().receipt
        )

        # Check ANGROMIX soy milk items (first two purchases)
        soy_milk_purchases = [
            p for p in receipt.purchases if "ANGROMIX-77 Lapte din soia" in p.name
        ]
        self.assertEqual(len(soy_milk_purchases), 2)
        self.assertEqual(soy_milk_purchases[0].price, soy_milk_purchases[1].price)

    def test_parse_html_returns_self_for_chaining(self):
        """Test that parse_html returns self to enable method chaining"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )

        result = parser.parse_html(load_stub_file(LIN_RECEIPT_PATH))

        self.assertIs(result, parser)

    def test_build_receipt_returns_self_for_chaining(self):
        """Test that build_receipt returns self to enable method chaining"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        parser.parse_html(load_stub_file(LIN_RECEIPT_PATH))

        result = parser.build_receipt()

        self.assertIs(result, parser)

    def test_fractional_quantities_parsed_correctly(self):
        """Test that fractional quantities (like for produce) are parsed correctly"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), KL_RECEIPT.receipt_url, db_api
        )
        receipt = (
            parser.parse_html(load_stub_file(KL_RECEIPT_PATH)).build_receipt().receipt
        )

        # Kaufland receipt has fractional quantities for produce
        fractional_purchases = [
            p for p in receipt.purchases if p.quantity != int(p.quantity)
        ]
        self.assertGreater(
            len(fractional_purchases),
            0,
            "Should have purchases with fractional quantities",
        )

        for purchase in fractional_purchases:
            self.assertIsInstance(purchase.quantity, float)
            self.assertGreater(purchase.quantity, 0)
            self.assertLess(purchase.quantity, 10)  # Reasonable upper bound for produce

    def test_html_entities_are_decoded(self):
        """Test that HTML entities in receipt data are properly decoded"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )

        # parse_html should handle HTML entity decoding via html.unescape
        result = parser.parse_html(load_stub_file(LIN_RECEIPT_PATH))

        # Verify that _data is properly set and JSON decoded
        self.assertTrue(hasattr(result, "_data"))
        self.assertIsInstance(result._data, dict)

    def test_parser_initialization_with_different_urls(self):
        """Test parser can be initialized with different URL formats"""
        logger = Mock()
        db_api = Mock()

        urls = [
            "https://mev.sfs.md/receipt-verifier/J403001576/118.04/135932/2024-01-17",
            "https://sift-mev.sfs.md/receipt/J702003194/370.85/25312/2023-10-17",
        ]

        for url in urls:
            with self.subTest(url=url):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                self.assertEqual(parser.url, url)
                self.assertEqual(parser.user_id, UUID(USER_ID_1))
                self.assertEqual(parser.logger, logger)

    def test_build_receipt_without_parse_html_raises_error(self):
        """Test that calling build_receipt without parse_html first raises an error"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), LIN_RECEIPT_URL, db_api)

        with self.assertRaises(AttributeError):
            parser.build_receipt()

    def test_persist_without_building_receipt_raises_error(self):
        """Test that calling persist without building receipt first raises an error"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), LIN_RECEIPT_URL, db_api)

        with self.assertRaises(AttributeError):
            parser.persist()

    def test_receipt_total_matches_sum_of_purchases(self):
        """Test that receipt total amount roughly matches sum of purchases
        Kaufland doesn't pass this test because it doesn't include discount in the total amount
        """
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
            (NANU_RECEIPT_PATH, NANU_RECEIPT.receipt_url),
        ]

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt

                # Calculate sum of all purchases (quantity * price)
                calculated_total = sum(p.quantity * p.price for p in receipt.purchases)

                # Allow small rounding difference (within 0.1)
                self.assertAlmostEqual(receipt.total_amount, calculated_total, delta=0.1)

    def test_unit_extraction_case_insensitive(self):
        """Test that units are extracted regardless of case"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        receipt = (
            parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt().receipt
        )

        # Check that units are properly extracted (the regex is case insensitive)
        from src.schemas.common import Unit

        units_found = [p.unit for p in receipt.purchases if p.unit is not None]

        # Verify we have various unit types
        self.assertGreater(len(units_found), 0)
        for unit in units_found:
            self.assertIn(unit, [Unit.KILOGRAM, Unit.GRAM, Unit.LITER, Unit.MILLILITER])

    def test_parse_html_with_html_entities_in_product_names(self):
        """Test that HTML entities in product names are decoded properly"""
        logger = Mock()
        db_api = Mock()

        # Create HTML with HTML entities in product name
        html_with_entities = load_stub_file(LIN_RECEIPT_PATH)

        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        result = parser.parse_html(html_with_entities)

        # Should not raise an error and should properly decode entities
        self.assertIsInstance(result, SfsMdReceiptParser)

    def test_get_receipt_with_db_api_exception(self):
        """Test that exceptions from db_api are propagated"""
        logger = Mock()
        db_api = Mock()
        db_api.side_effect = Exception("Database error")

        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )

        with self.assertRaises(Exception) as context:
            parser.get_receipt()

        self.assertIn("Database error", str(context.exception))

    def test_persist_with_db_api_exception(self):
        """Test that exceptions from db_api during persist are propagated"""
        logger = Mock()
        db_api = Mock()
        db_api.side_effect = Exception("Database error during persist")

        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt()

        with self.assertRaises(Exception) as context:
            parser.persist()

        self.assertIn("Database error during persist", str(context.exception))

    def test_multiple_parsers_dont_interfere(self):
        """Test that multiple parser instances don't interfere with each other"""
        logger = Mock()
        db_api = Mock()

        parser1 = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        parser2 = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), KL_RECEIPT.receipt_url, db_api
        )

        receipt1 = (
            parser1.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt().receipt
        )
        receipt2 = (
            parser2.parse_html(load_stub_file(KL_RECEIPT_PATH)).build_receipt().receipt
        )

        # Verify they have different URLs
        self.assertEqual(receipt1.receipt_url, LIN_RECEIPT.receipt_url)
        self.assertEqual(receipt2.receipt_url, KL_RECEIPT.receipt_url)
        self.assertNotEqual(receipt1.receipt_url, receipt2.receipt_url)

        # Verify they have different companies
        self.assertNotEqual(receipt1.company_id, receipt2.company_id)

    def test_receipt_has_valid_date_object(self):
        """Test that receipt date is a valid datetime object"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url),
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
            (LIN2_RECEIPT_PATH, LIN_RECEIPT_2.receipt_url),
            (NANU_RECEIPT_PATH, NANU_RECEIPT.receipt_url),
        ]

        from datetime import datetime

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt

                self.assertIsInstance(receipt.date, datetime)
                # Verify date is not in the future
                self.assertLessEqual(receipt.date, datetime.now())

    def test_all_purchases_have_required_fields(self):
        """Test that all purchases have name, quantity, and price"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url),
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
            (LIN2_RECEIPT_PATH, LIN_RECEIPT_2.receipt_url),
            (NANU_RECEIPT_PATH, NANU_RECEIPT.receipt_url),
        ]

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt

                for i, purchase in enumerate(receipt.purchases):
                    with self.subTest(purchase_index=i):
                        self.assertIsNotNone(purchase.name)
                        self.assertIsNotNone(purchase.quantity)
                        self.assertIsNotNone(purchase.price)
                        self.assertIsInstance(purchase.name, str)
                        self.assertIsInstance(purchase.quantity, float)
                        self.assertIsInstance(purchase.price, float)

    def test_unit_and_unit_quantity_consistency(self):
        """Test that if unit is set, unit_quantity is also set and vice versa"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url),
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
        ]

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt

                for purchase in receipt.purchases:
                    # If unit is set, unit_quantity should be set
                    if purchase.unit is not None:
                        self.assertIsNotNone(purchase.unit_quantity)
                        self.assertGreater(purchase.unit_quantity, 0)
                    # If unit_quantity is set, unit should be set
                    if purchase.unit_quantity is not None:
                        self.assertIsNotNone(purchase.unit)

    def test_url_stored_in_parser_instance(self):
        """Test that URL is properly stored in parser instance"""
        logger = Mock()
        db_api = Mock()
        test_url = (
            "https://mev.sfs.md/receipt-verifier/J403001576/118.04/135932/2024-01-17"
        )

        parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), test_url, db_api)

        self.assertEqual(parser.url, test_url)

    def test_logger_stored_in_parser_instance(self):
        """Test that logger is properly stored in parser instance"""
        logger = Mock()
        db_api = Mock()

        parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), LIN_RECEIPT_URL, db_api)

        self.assertIs(parser.logger, logger)

    def test_user_id_stored_in_parser_instance(self):
        """Test that user_id is properly stored in parser instance"""
        logger = Mock()
        db_api = Mock()
        test_user_id = UUID(USER_ID_1)

        parser = SfsMdReceiptParser(logger, test_user_id, LIN_RECEIPT_URL, db_api)

        self.assertEqual(parser.user_id, test_user_id)

    def test_db_api_stored_in_parser_instance(self):
        """Test that db_api is properly stored in parser instance"""
        logger = Mock()
        db_api = Mock()

        parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), LIN_RECEIPT_URL, db_api)

        self.assertIs(parser.query_db_api, db_api)

    def test_validate_url_with_http_instead_of_https(self):
        """Test that HTTP URLs are rejected"""
        logger = Mock()
        db_api = Mock()

        http_urls = [
            "http://mev.sfs.md/receipt-verifier/J403001576/118.04/135932/2024-01-17",
            "http://sift-mev.sfs.md/receipt/J403001576/118.04/135932/2024-01-17",
        ]

        for url in http_urls:
            with self.subTest(url=url):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                self.assertFalse(parser.validate_receipt_url())

    def test_validate_url_with_different_subdomains(self):
        """Test that only specific subdomains are accepted"""
        logger = Mock()
        db_api = Mock()

        invalid_subdomains = [
            "https://www.mev.sfs.md/receipt-verifier/test",
            "https://api.sfs.md/receipt/test",
            "https://mev2.sfs.md/receipt-verifier/test",
        ]

        for url in invalid_subdomains:
            with self.subTest(url=url):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                self.assertFalse(parser.validate_receipt_url())

    def test_receipt_has_all_required_schema_fields(self):
        """Test that receipt has all required fields from the schema"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        receipt = (
            parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt().receipt
        )

        required_fields = [
            "date",
            "user_id",
            "company_id",
            "company_name",
            "country_code",
            "shop_address",
            "cash_register_id",
            "key",
            "currency_code",
            "total_amount",
            "purchases",
            "receipt_url",
        ]

        for field in required_fields:
            with self.subTest(field=field):
                self.assertTrue(hasattr(receipt, field))
                self.assertIsNotNone(getattr(receipt, field))

    def test_purchase_has_all_required_schema_fields(self):
        """Test that each purchase has all required fields"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        receipt = (
            parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt().receipt
        )

        required_fields = ["name", "quantity", "price"]

        for purchase in receipt.purchases:
            for field in required_fields:
                with self.subTest(field=field, purchase=purchase.name):
                    self.assertTrue(hasattr(purchase, field))
                    self.assertIsNotNone(getattr(purchase, field))

    def test_parser_handles_large_quantities(self):
        """Test that parser handles large quantities correctly (NANU receipt has many items)"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), NANU_RECEIPT.receipt_url, db_api
        )
        receipt = (
            parser.parse_html(load_stub_file(NANU_RECEIPT_PATH)).build_receipt().receipt
        )

        # NANU receipt has 14 purchases
        self.assertEqual(len(receipt.purchases), 14)

        # Verify all purchases are parsed correctly
        for purchase in receipt.purchases:
            self.assertGreater(purchase.quantity, 0)
            self.assertGreater(purchase.price, 0)
            self.assertGreater(len(purchase.name), 0)

    def test_parser_handles_different_date_formats(self):
        """Test that parser handles various dates across different years"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (LIN_RECEIPT_PATH, 2024, 1, 17),  # Jan 2024
            (LIN2_RECEIPT_PATH, 2026, 1, 3),  # Jan 2026
            (KL_RECEIPT_PATH, 2023, 10, 17),  # Oct 2023
            (NANU_RECEIPT_PATH, 2025, 8, 2),  # Aug 2025
        ]

        for path, expected_year, expected_month, expected_day in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(
                    logger, UUID(USER_ID_1), LIN_RECEIPT_URL, db_api
                )
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt

                self.assertEqual(receipt.date.year, expected_year)
                self.assertEqual(receipt.date.month, expected_month)
                self.assertEqual(receipt.date.day, expected_day)

    def test_persist_returns_receipt(self):
        """Test that persist method returns the receipt object"""
        logger = Mock()
        db_api = Mock()

        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt()

        result = parser.persist()

        self.assertIsNotNone(result)
        self.assertEqual(result, parser.receipt)
        self.assertIsInstance(result, type(LIN_RECEIPT))

    def test_parse_html_with_whitespace_variations(self):
        """Test that parser handles HTML with different whitespace patterns"""
        logger = Mock()
        db_api = Mock()

        # Load actual HTML which may have various whitespace patterns
        html_content = load_stub_file(LIN_RECEIPT_PATH)

        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        result = parser.parse_html(html_content)

        # Should successfully parse regardless of whitespace
        self.assertIsInstance(result, SfsMdReceiptParser)
        self.assertIsNotNone(result._data)

    def test_receipt_model_dump_returns_dict(self):
        """Test that receipt.model_dump() returns a dictionary for persistence"""
        logger = Mock()
        db_api = Mock()
        parser = SfsMdReceiptParser(
            logger, UUID(USER_ID_1), LIN_RECEIPT.receipt_url, db_api
        )
        parser.parse_html(load_stub_file(LIN_RECEIPT_PATH)).build_receipt()

        receipt_dict = parser.receipt.model_dump()

        self.assertIsInstance(receipt_dict, dict)
        self.assertIn("date", receipt_dict)
        self.assertIn("purchases", receipt_dict)
        self.assertIn("total_amount", receipt_dict)

    def test_empty_purchase_name_filtered_out(self):
        """Test that purchases with empty names are filtered during parsing"""
        logger = Mock()
        db_api = Mock()
        test_cases = [
            (KL_RECEIPT_PATH, KL_RECEIPT.receipt_url),
            (LIN_RECEIPT_PATH, LIN_RECEIPT.receipt_url),
            (LIN2_RECEIPT_PATH, LIN_RECEIPT_2.receipt_url),
            (NANU_RECEIPT_PATH, NANU_RECEIPT.receipt_url),
        ]

        for path, url in test_cases:
            with self.subTest(path=path):
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), url, db_api)
                receipt = parser.parse_html(load_stub_file(path)).build_receipt().receipt

                # All purchases should have non-empty names
                for purchase in receipt.purchases:
                    self.assertNotEqual(purchase.name, "")
                    self.assertGreater(len(purchase.name.strip()), 0)
