import json
import os
from http import HTTPStatus
from unittest import TestCase
from unittest.mock import Mock

import requests

from src.adapters.db.cosmos_db_core import CosmosDBCoreAdapter
from src.schemas.common import EnvType, TableName, TablePartitionKey, CountryCode
from src.tests import USER_ID_1, SHOP_ITEM_ID_1, BARCODE_1, SHOP_ID_1

RECEIPT_URL = "https://mev.sfs.md/receipt-verifier/B93BDE722E208AACBA2E85E4EF754E5E"
RECEIPT_ID = "md_j403001574_97568"
KL_NODE_URL = "https://www.openstreetmap.org/node/10239783211"


class TestStaticPages(TestCase):
    def test_tos(self):
        response = requests.get(
            f"https://{os.environ['WEBSITE_HOSTNAME']}/terms-of-service", timeout=5
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)


# class TestHome(TestCase):
#     # doesn't require db adapter
#     def test_home(self):
#         response = requests.get(f"https://{os.environ['WEBSITE_HOSTNAME']}/home", timeout=5)
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#
# class TestFunctionApp(TestCase):
#     session = None
#
#     @classmethod
#     def setUpClass(cls):
#         logger = Mock()
#         cls.host = os.environ["WEBSITE_HOSTNAME"]
#         cls.session = CosmosDBCoreAdapter(EnvType.TEST, logger)
#
#     def setUp(self):
#         for table_name, partition_key in list(zip(TableName, TablePartitionKey)):
#             self.session.create_table(table_name, partition_key=partition_key)
#
#     def tearDown(self):
#         for table_name in TableName:
#             self.session.drop_table(TableName(table_name))
#
#     def test_parse_from_url(self):
#         data = {"url": RECEIPT_URL, "user_id": USER_ID_1}
#         response = requests.post(f"{self.host}/parse-from-url", data=data, timeout=5)
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_link_shop(self):
#         self.session.use_table(TableName.RECEIPT)
#         self.session.create_one(
#             {
#                 "_id": RECEIPT_ID,
#                 "user_id": USER_ID_1,
#                 "country_code": CountryCode.MOLDOVA,
#                 "shop_address": "test_shop_address",
#                 "company_id": "test_company_id",
#             }
#         )
#
#         data = {
#             "url": KL_NODE_URL,
#             "user_id": USER_ID_1,
#             "receipt_id": RECEIPT_ID,
#         }
#         response = requests.post(f"{self.host}/link-shop", data=data, timeout=5)
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_add_barcodes(self):
#         items = json.dumps(
#             [
#                 {
#                     "item_id": SHOP_ITEM_ID_1,
#                     "purchase_id": "test_purchase_1",
#                     "status": "pending",
#                     "barcode": BARCODE_1,
#                 }
#             ]
#         )
#         data = {"shop_id": SHOP_ID_1, "items": items}
#         response = requests.post(f"{self.host}/add-barcodes", data=data, timeout=5)
#         self.assertEqual(response.status_code, HTTPStatus.OK)
