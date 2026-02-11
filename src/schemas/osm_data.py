from src.helpers.osm import get_osm_id
from src.schemas.common import OsmType
from src.schemas.schema_base import SchemaBase


class OsmData(SchemaBase):
    id: str | None = None
    type: OsmType
    key: int  # unique only within each type
    lat: str
    lon: str
    display_name: str | None = None
    address: dict | None = None

    def model_post_init(self, __context) -> None:
        self.id = get_osm_id(self.type, str(self.key))
