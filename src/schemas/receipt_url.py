from src.helpers.common import make_hash
from src.schemas.common import CountryCode
from src.schemas.schema_base import SchemaBase


class ReceiptUrl(SchemaBase):
    id: str
    url: str
    receipt_id: str
    country_code: CountryCode

    def model_post_init(self, __context) -> None:
        self.id = make_hash(self.url)
