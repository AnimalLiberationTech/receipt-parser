"""Barcode validation and types."""

from enum import Enum
from pydantic import field_validator

from src.schemas.schema_base import SchemaBase


class BarcodeType(Enum):
    UPC_A = 12
    UPC_E = 7
    EAN_8 = 8
    EAN_13 = 13


def generate_checkdigit(code: int) -> int:
    """Generate check digit for a barcode."""
    digits = [int(d) for d in str(code)]
    for i in range(0, len(digits), 2):
        digits[i] *= 3
    checkdigit = (10 - (sum(digits) % 10)) % 10
    return checkdigit


def validate_upc(code) -> bool:
    """Validate a UPC/EAN barcode check digit."""
    digits = str(code)
    try:
        check_digit = int(digits[-1])
        calculated = generate_checkdigit(int(digits[:-1]))
        return check_digit == calculated
    except (ValueError, IndexError):
        return False


class Barcode(SchemaBase):
    """Barcode model with validation."""

    code: int
    type: BarcodeType

    @field_validator("code")
    @classmethod
    def validate_code(cls, v, info):
        if not isinstance(v, int):
            raise ValueError("code must be an integer")
        return v

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v):
        if isinstance(v, str):
            return BarcodeType[v]
        return v

    def model_post_init(self, __context):
        # Validate barcode length matches type
        if len(str(self.code)) != self.type.value:
            raise ValueError(
                f"code must be {self.type.value} digits long, got {len(str(self.code))}"
            )
        # Validate check digit
        if not validate_upc(self.code):
            raise ValueError("invalid barcode")

    def __repr__(self):
        return str(self.code)

