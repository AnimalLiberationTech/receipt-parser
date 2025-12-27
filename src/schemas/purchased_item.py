from uuid import UUID

from src.schemas.common import ItemBarcodeStatus
from src.schemas.schema_base import SchemaBase


class PurchasedItem(SchemaBase):
    name: str
    quantity: float
    price: float
    item_id: UUID | None = None
    status: ItemBarcodeStatus = ItemBarcodeStatus.PENDING
