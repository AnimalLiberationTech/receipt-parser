from http import HTTPStatus
from typing import Any, Callable
from uuid import UUID

from src.helpers.osm import lookup_osm_data
from src.schemas.common import OsmType, ApiResponse
from src.schemas.osm_data import OsmData
from src.schemas.request_schemas import AddShopPayload
from src.schemas.shop import Shop


def link_shop_handler(
    osm_type: OsmType,
    osm_key: int,
    receipt_id: str,
    logger: Any,
    db_api: Callable[[str, str, Any], Any],
) -> ApiResponse:
    osm_shop_data = lookup_osm_data(osm_type, osm_key)
    if not osm_shop_data:
        return ApiResponse(
            status_code=HTTPStatus.BAD_REQUEST, detail="Failed to get OSM shop details"
        )

    resp = db_api("/receipt/get-by-id", "GET", query={"receipt_id": receipt_id})
    logger.info(resp)
    if not resp or resp.get("status_code") != HTTPStatus.OK:
        logger.error(f"Failed to get receipt with id {receipt_id}")
        return ApiResponse(
            status_code=HTTPStatus.BAD_REQUEST, detail="Failed to get the receipt"
        )

    receipt = resp["data"]
    osm_data = OsmData(
        type=osm_type,
        key=osm_key,
        lat=osm_shop_data["lat"],
        lon=osm_shop_data["lon"],
        display_name=osm_shop_data["display_name"],
        address=osm_shop_data["address"],
    )
    shop = Shop(
        country_code=receipt["country_code"],
        company_id=receipt["company_id"],
        address=receipt["shop_address"],
        osm_data=osm_data,
        creator_user_id=UUID(receipt["user_id"]),
    )
    logger.info(shop.model_dump(mode="json"))
    resp = db_api("/shop/get-or-create", "POST", shop.model_dump(mode="json"))
    logger.info(resp)
    if not resp or resp.get("status_code") != HTTPStatus.OK:
        logger.error("Failed to get or create shop")
        return ApiResponse(
            status_code=HTTPStatus.BAD_REQUEST, detail="Failed to get or create shop"
        )

    shop = resp["data"]

    payload = AddShopPayload(shop_id=shop["id"], receipt=receipt)
    resp = db_api("/receipt/add-shop-id", "POST", payload.model_dump(mode="json"))
    logger.info(resp)
    if not resp or resp.get("status_code") != HTTPStatus.OK:
        logger.error("Failed to add shop id to receipt")
        return ApiResponse(
            status_code=HTTPStatus.BAD_REQUEST, detail="Failed to add shop id to receipt"
        )

    return ApiResponse(
        status_code=HTTPStatus.OK,
        detail="Shop successfully linked",
        data={"shop_id": shop["id"]},
    )
