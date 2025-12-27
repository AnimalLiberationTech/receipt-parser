from typing import Optional
from uuid import UUID, uuid4

from pydantic import Field

from src.schemas.common import CountryCode
from src.schemas.osm_object import OsmObject
from src.schemas.schema_base import SchemaBase


class Shop(SchemaBase):
    id: Optional[UUID] = Field(default_factory=uuid4)
    country_code: CountryCode
    company_id: str
    shop_address: str
    osm_object: OsmObject
