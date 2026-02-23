import html
import json
import re
from datetime import datetime
from http import HTTPStatus
from typing import Self, Callable, Any
from uuid import UUID

from src.helpers.common import split_list
from src.parsers.receipt_parser_base import ReceiptParserBase
from src.schemas.common import CountryCode, CurrencyCode, Unit
from src.schemas.purchased_item import PurchasedItem
from src.schemas.sfs_md.receipt import SfsMdReceipt

RECEIPT_REGEX = r'wire:initial-data="([^"]*receipt\.index-component[^"]*)"'
QUANTITY_UNITS_REGEX = r"(?i)(\d+(\.\d+)?)\s*(kg|g|ml|l)(?![A-Za-z])|(kg\s+[A-Za-z]+)"


class SfsMdReceiptParser(ReceiptParserBase):
    _data: dict
    receipt: SfsMdReceipt
    url: str

    def __init__(
        self, logger, user_id: UUID, url: str, db_api: Callable[[str, str, Any], Any]
    ):
        self.logger = logger
        self.user_id = user_id
        self.url = url
        self.query_db_api = db_api

    async def get_receipt(self) -> SfsMdReceipt | None:
        resp = await self.query_db_api("/receipt/get-by-url", "POST", {"url": self.url})

        if not isinstance(resp, dict):
            self.logger.error(
                f"Invalid db_api response: expected dict, got {type(resp).__name__}"
            )
            raise ValueError("Invalid Plant-Based API response")

        if resp.get("status_code") != HTTPStatus.OK:
            detail = resp.get("detail", "Unknown error")
            raise ValueError(f"Failed to get receipt: {detail}")

        if resp.get("data"):
            return SfsMdReceipt(**resp.get("data"))

        return None

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
                unit_groups = re.search(QUANTITY_UNITS_REGEX, purchase[0])
                unit = None
                unit_quantity = None
                if unit_groups:
                    # Guard against alternate regex branches where quantity/unit groups are missing
                    quantity_group = unit_groups.group(1)
                    unit_group = unit_groups.group(3)
                    if quantity_group is not None and unit_group is not None:
                        try:
                            unit_quantity = float(quantity_group)
                            unit_str = unit_group.lower()
                            unit = Unit(unit_str)
                        except ValueError:
                            # Leave unit and unit_quantity as None if parsing fails
                            pass

                purchases.append(
                    PurchasedItem(
                        name=purchase[0],
                        quantity=float(quantity),
                        unit=unit,
                        unit_quantity=unit_quantity,
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

    async def persist(self) -> SfsMdReceipt:
        receipt = self.receipt.model_dump(mode="json")
        self.logger.info(receipt)

        resp = await self.query_db_api("/receipt/get-or-create", "POST", receipt)

        if not isinstance(resp, dict):
            self.logger.error(
                f"Invalid db_api response: expected dict, got {type(resp).__name__}"
            )
            raise ValueError("Invalid Plant-Based API response")

        if resp.get("status_code") != HTTPStatus.OK:
            detail = resp.get("detail", "Unknown error")
            raise ValueError(f"Failed to persist receipt: {detail}")

        return self.receipt

    def validate_receipt_url(self) -> bool:
        return any(
            self.url.startswith(host)
            for host in [
                "https://mev.sfs.md/receipt-verifier/",
                "https://sift-mev.sfs.md/receipt/",
            ]
        )
