import json
from uuid import UUID

from src.adapters.db.cosmos_db_core import init_db_session
from src.schemas.common import TableName, ItemBarcodeStatus
from src.schemas.shop_item import ShopItem


def add_barcodes_handler(shop_id: str, items: list[dict], logger) -> (int, dict):
    session = init_db_session(logger)
    session.use_table(TableName.SHOP_ITEM)

    invalid_items = []
    for item in items:
        try:
            item = ShopItem(
                id=UUID(item["item_id"]) if item.get("item_id") else None,
                shop_id=UUID(shop_id),
                name="_".join(item["purchase_id"].split("_")[:-1]),
                status=ItemBarcodeStatus(item["status"]),
                barcode=item.get("barcode"),
            ).to_dict()
            session.create_or_update_one(item)
        except ValueError as e:
            invalid_items.append({"name": item["name"], "error": str(e)})
            logger.error(f"Failed to add item: {json.dumps(item)}. Error: {e}")

    if invalid_items:
        return 400, {"msg": "Failed to add some items", "invalid_items": invalid_items}
    return 200, {"msg": "Purchases successfully added. You can add another URL"}
