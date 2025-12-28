from http import HTTPStatus
from uuid import UUID

from src.helpers.common import get_html
from src.parsers.sfs_md.receipt_parser import SfsMdReceiptParser


def parse_from_url_handler(url: str, user_id: str, logger) -> (HTTPStatus, dict):
    if not url:
        return HTTPStatus.BAD_REQUEST, {"msg": "URL is required"}

    try:
        user_id = UUID(user_id)
    except ValueError:
        return HTTPStatus.BAD_REQUEST, {"msg": "Invalid user ID"}

    parser = SfsMdReceiptParser(logger)
    if not parser.validate_receipt_url(url):
        return HTTPStatus.BAD_REQUEST, {"msg": "Unsupported URL"}

    receipt_html = get_html(url, logger)
    if not receipt_html:
        return HTTPStatus.BAD_REQUEST, {"msg": "Failed to fetch receipt"}

    try:
        receipt = parser.parse_html(receipt_html).build_receipt(user_id).persist()
    except ValueError as e:
        return HTTPStatus.BAD_REQUEST, {"msg": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error parsing receipt: {e}")
        return HTTPStatus.INTERNAL_SERVER_ERROR, {"msg": "Internal server error"}

    return HTTPStatus.OK, {
        "msg": "Receipt successfully processed",
        "data": receipt.model_dump(mode="json"),
    }
