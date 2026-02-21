import os

USER_ID_1 = "235baf90-f7a8-43a0-bf86-e9d6593d397d"
SHOP_ID_1 = "74000"
SHOP_ITEM_ID_1 = "5fbee799-c8fc-4207-8b1f-4f2af0ceca9d"
BARCODE_1 = "8076809501965"
SESSION_ID = "7c30e8c6-cb7b-41b2-a028-82563761d7b9"
STATE_ID = "state"


def get_stub_file_path(rel_path: str) -> str:
    dir_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir_path, "stubs", rel_path)


def load_stub_file(rel_path: str) -> str:
    with open(get_stub_file_path(rel_path), "r", encoding="utf8") as file:
        file = file.read()
    return file
