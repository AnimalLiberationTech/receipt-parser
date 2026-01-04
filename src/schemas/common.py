from enum import StrEnum, Enum


class EnvType(StrEnum):
    PROD = "prod"
    STAGE = "stage"
    DEV = "dev"
    TEST = "test"
    LOCAL = "local"


class TableName(StrEnum):
    RECEIPT = "receipt"
    RECEIPT_URL = "receipt_url"
    PURCHASED_ITEM = "purchased_item"
    SHOP = "shop"
    SHOP_ITEM = "shop_item"
    USER = "user"
    USER_IDENTITY = "user_identity"
    USER_SESSION = "user_session"


class TablePartitionKey(StrEnum):
    RECEIPT = "user_id"
    RECEIPT_URL = "country_code"
    SHOP = "country_code"
    SHOP_ITEM = "shop_id"
    USER = "banned"
    USER_IDENTITY = "provider"
    USER_SESSION = "identity_provider"


class CountryCode(StrEnum):
    MOLDOVA = "md"


# https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-one.xml
class CurrencyCode(StrEnum):
    MOLDOVAN_LEU = "mdl"


class OsmType(StrEnum):
    NODE = "node"
    WAY = "way"
    RELATION = "relation"


class ReceiptProvider(StrEnum):
    SFS_MD = "sfs_md"


class QuantityUnit(StrEnum):
    PIECE = "pcs"      # pieces/units
    KILOGRAM = "kg"    # kilograms
    GRAM = "g"         # grams
    LITER = "l"        # liters
    MILLILITER = "ml"  # milliliters
    METER = "m"        # meters
    CENTIMETER = "cm"  # centimeters


class ItemBarcodeStatus(StrEnum):
    PENDING = "pending"  # barcode is not yet added
    MISSING = "missing"  # item does not have international barcode
    IRRELEVANT = "irrelevant"  # item is not relevant for the app users (e.g. car tyres)
    ADDED = "added"  # barcode is added by the user


class Operator(Enum):
    EQ = "eq"
    NE = "ne"
