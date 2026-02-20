from http import HTTPStatus
from typing import Any, Callable
from uuid import UUID

from src.helpers.common import get_html
from src.parsers.sfs_md.receipt_parser import SfsMdReceiptParser
from src.schemas.common import ApiResponse


def parse_from_url_handler(
    url: str, user_id: UUID, logger: Any, db_api: Callable[[str, str, Any], Any]
) -> ApiResponse:
    parser = SfsMdReceiptParser(logger, user_id, url, db_api)
    if not parser.validate_receipt_url():
        return ApiResponse(status_code=HTTPStatus.BAD_REQUEST, detail="Unsupported URL")

    try:
        receipt = parser.get_receipt()
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Error retrieving receipt: {e}")
        return ApiResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Error retrieving receipt",
        )

    if receipt:
        logger.info("Receipt found in the db")
    else:
        receipt_html = get_html(url, logger)
        if not receipt_html:
            return ApiResponse(
                status_code=HTTPStatus.BAD_REQUEST, detail="Failed to fetch receipt"
            )

        try:
            receipt = parser.parse_html(receipt_html).build_receipt().persist()
        except ValueError as e:
            return ApiResponse(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Unexpected error parsing receipt: {e}")
            return ApiResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    return ApiResponse(
        status_code=HTTPStatus.OK,
        detail="Receipt successfully processed",
        data=receipt.model_dump(mode="json"),
    )
