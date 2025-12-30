import html
import json
import re
from datetime import datetime
from typing import Self
from uuid import UUID

from src.adapters.db.cosmos_db_core import init_db_session
from src.helpers.common import split_list, make_hash
from src.parsers.receipt_parser_base import ReceiptParserBase
from src.schemas.common import CountryCode, TableName, ItemBarcodeStatus, CurrencyCode
from src.schemas.purchased_item import PurchasedItem
from src.schemas.sfs_md.receipt import SfsMdReceipt
from src.schemas.receipt_url import ReceiptUrl

RECEIPT_REGEX = r'wire:initial-data="([^"]*receipt\.index-component[^"]*)"'


class SfsMdReceiptParser(ReceiptParserBase):
    _data: dict
    receipt: SfsMdReceipt
    url: str

    def __init__(self, logger, user_id: UUID, url: str):
        self.logger = logger
        self.user_id = user_id
        self.url = url
        self.session = init_db_session(logger)

    def parse_html(self, page: str) -> Self:
        matches = re.search(RECEIPT_REGEX, page)
        if matches:
            self._data = json.loads(html.unescape(matches.group(1)))
        else:
            self.logger.warning(
                f"Failed to parse receipt data. " f"Page content preview: {page[:200]}"
            )
            raise ValueError("Failed to parse receipt data from HTML")
        return self

    def build_receipt(self) -> Self:
        data = split_list(
            self._data["serverMemo"]["data"]["receipt"],
            "````````````````````````````````````````````````",
        )
        date_str = data[-2][0][0][5:] + data[-2][0][1][3:]
        date = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")

        purchases = []
        for purchase in data[1]:
            if purchase[0] != "":
                quantity, price = purchase[1].split(" x ")
                purchases.append(
                    PurchasedItem(
                        name=purchase[0],
                        quantity=float(quantity),
                        price=float(price),
                    )
                )

        self.receipt = SfsMdReceipt(
            id=None,
            date=date,
            user_id=self.user_id,
            company_id=data[0][1][12:],
            company_name=data[0][0],
            country_code=CountryCode.MOLDOVA,
            shop_address=data[0][2],
            cash_register_id=data[0][3][25:],
            key=int(data[-1][0][1]),
            currency_code=CurrencyCode.MOLDOVAN_LEU,
            total_amount=float(data[2][0][1]),
            purchases=purchases,
            receipt_url=self.url,
        )
        return self

    def persist(self) -> SfsMdReceipt:
        self.session.use_table(TableName.SHOP)
        shops = self.session.read_many(
            {
                "shop_address": self.receipt.shop_address,
                "company_id": self.receipt.company_id,
            },
            partition_key=CountryCode.MOLDOVA,
            limit=1,
        )
        if shops:
            self.receipt.shop_id = shops[0]["id"]

            for i, purchase in enumerate(self.receipt.purchases):
                self.session.use_table(TableName.SHOP_ITEM)
                items = self.session.read_many(
                    {"name": purchase.name}, partition_key=self.receipt.shop_id, limit=1
                )
                if items:
                    self.receipt.purchases[i].item_id = items[0]["id"]
                    self.receipt.purchases[i].status = items[0].get(
                        "status", ItemBarcodeStatus.PENDING
                    )

        self.session.use_table(TableName.RECEIPT)
        self.session.create_or_update_one(self.receipt.model_dump(mode="json"))

        self.session.use_table(TableName.RECEIPT_URL)
        receipt_url = ReceiptUrl(url=self.url, receipt_id=self.receipt.id, country_code=CountryCode.MOLDOVA)
        self.session.create_one(receipt_url.model_dump(mode="json"))
        receipt_url.url = self.receipt.receipt_canonical_url
        self.session.create_one(receipt_url.model_dump(mode="json"))

        self.logger.info(self.receipt.model_dump())
        return self.receipt

    def get_receipt(self) -> SfsMdReceipt | None:
        self.session.use_table(TableName.RECEIPT_URL)
        receipt_url = self.session.read_one(
            make_hash(self.url), partition_key=CountryCode.MOLDOVA
        )
        if receipt_url:
            self.session.use_table(TableName.RECEIPT)
            receipt = self.session.read_one(
                receipt_url["receipt_id"], partition_key=str(self.user_id)
            )
            if receipt:
                return SfsMdReceipt(**receipt)
        return None

    def validate_receipt_url(self) -> bool:
        return any(
            self.url.startswith(host)
            for host in [
                "https://mev.sfs.md/receipt-verifier/",
                "https://sift-mev.sfs.md/receipt/",
            ]
        )
