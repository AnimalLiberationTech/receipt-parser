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
                parser = SfsMdReceiptParser(logger, UUID(USER_ID_1), expected.receipt_url)
                self.assertEqual(
                    parser.parse_html(load_stub_file(path)).build_receipt().receipt,
                    expected,
                )
