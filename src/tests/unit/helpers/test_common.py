from unittest import TestCase

from src.helpers.common import split_list, validate_barcode


class TestCommon(TestCase):
    def test_split_list(self):
        self.assertEqual(
            split_list([1, 2, 3, None, 4, 5, None, 6], None), [[1, 2, 3], [4, 5], [6]]
        )
        self.assertEqual(
            split_list(["a", "b", "c", "d", "e"], "c"), [["a", "b"], ["d", "e"]]
        )
        self.assertEqual(split_list([], None), [])

    def test_validate_barcode(self):
        valid_code_13 = "1234567890128"
        self.assertTrue(validate_barcode("1234567890128"))
        valid_code_8 = "12345678"
        self.assertTrue(validate_barcode(valid_code_8))

        short_code = valid_code_8[:-1]
        self.assertFalse(validate_barcode(short_code))
        long_code = valid_code_13 + "99"
        self.assertFalse(validate_barcode(long_code))
        invalid_char_code = valid_code_13[:-1] + "a"
        self.assertFalse(validate_barcode(invalid_char_code))
        invalid_code_13 = valid_code_13[:-1] + "9"
        self.assertFalse(validate_barcode(invalid_code_13))
        valid_code_with_spaces = "1234 5678 9012 8"
        self.assertFalse(validate_barcode(valid_code_with_spaces))
