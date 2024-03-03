import os

from jinja2 import Environment, FileSystemLoader

from src.schemas.common import ItemBarcodeStatus


def home_handler() -> (int, str):
    file_loader = FileSystemLoader(os.path.join("src", "static", "templates"))
    jinja = Environment(loader=file_loader)
    data = {
        "route": {
            "parse": "parse-from-url",
            "link_shop": "link-shop",
            "add_barcodes": "add-barcodes",
        },
        "barcode_status": {
            status.name.lower(): status.value for status in ItemBarcodeStatus
        },
    }
    return 200, jinja.get_template("home.html").render(data)
