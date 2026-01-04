from uuid import UUID

from src.schemas.common import ItemBarcodeStatus, QuantityUnit
from src.schemas.schema_base import SchemaBase


class PurchasedItem(SchemaBase):
    name: str
    quantity: float
    quantity_unit: QuantityUnit | None = None
    price: float
    item_id: UUID | None = None
    status: ItemBarcodeStatus = ItemBarcodeStatus.PENDING
