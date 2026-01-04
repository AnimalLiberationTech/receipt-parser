from src.helpers.common import make_hash
from src.schemas.schema_base import SchemaBase


class ReceiptUrl(SchemaBase):
    id: str | None = None
    url: str
    receipt_id: str

    def model_post_init(self, __context) -> None:
        self.id = make_hash(self.url)
