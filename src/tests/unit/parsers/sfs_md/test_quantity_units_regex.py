import re
from unittest import TestCase

from src.parsers.sfs_md.receipt_parser import QUANTITY_UNITS_REGEX


class TestQuantityUnitsRegex(TestCase):
    def _assert_match(self, text: str, expected_qty: float, expected_unit: str):
        m = re.search(QUANTITY_UNITS_REGEX, text)
        self.assertIsNotNone(m, msg=f"No match for: {text}")
        qty = float(m.group(1))
        unit = m.group(3).lower()
        self.assertAlmostEqual(qty, expected_qty)
        self.assertEqual(unit, expected_unit)

    def test_lowercase_units(self):
        self._assert_match("Juice 1l", 1.0, "l")
        self._assert_match("Oil 330ml", 330.0, "ml")
        self._assert_match("Nuts 200 g", 200.0, "g")
        self._assert_match("Apples 1 kg", 1.0, "kg")

    def test_uppercase_units(self):
        self._assert_match("Milk 0.5 L", 0.5, "l")
        self._assert_match("SUGAR 250G", 250.0, "g")
        self._assert_match("FLOUR 1 KG", 1.0, "kg")
        self._assert_match("WATER 1L", 1.0, "l")

    def test_no_match(self):
        self.assertIsNone(re.search(QUANTITY_UNITS_REGEX, "No unit here"))
        self.assertIsNone(re.search(QUANTITY_UNITS_REGEX, "abc kgdef"))
