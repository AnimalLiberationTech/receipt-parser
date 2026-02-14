from uuid import UUID

from src.schemas.common import ItemBarcodeStatus, Unit
from src.schemas.schema_base import SchemaBase


class PurchasedItem(SchemaBase):
    name: str
    quantity: float
    unit: Unit | None = None
    unit_quantity: float | None = None
    price: float
    item_id: UUID | None = None
    status: ItemBarcodeStatus = ItemBarcodeStatus.PENDING
