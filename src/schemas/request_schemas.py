from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from src.schemas.common import OsmType
from src.schemas.sfs_md.receipt import SfsMdReceipt
from src.schemas.user_identity import IdentityProvider


class ParseFromUrlRequest(BaseModel):
    url: str
    user_id: UUID


class GetReceiptByUrlRequest(BaseModel):
    url: str


class LinkShopRequest(BaseModel):
    osm_type: OsmType
    osm_key: int
    receipt_id: str


class AddBarcodesRequest(BaseModel):
    shop_id: int
    items: list


class GetOrCreateUserByIdentityRequest(BaseModel):
    id: str
    provider: IdentityProvider
    email: Optional[EmailStr] = None
    name: str

class AddShopPayload(BaseModel):
    shop_id: int
    receipt: SfsMdReceipt