# algorithm description source: https://www.ibm.com/docs/en/zos/2.3.0?topic=parameters-check-digit-calculation-method
from enum import Enum
from dataclasses import dataclass


class BarcodeType(Enum):
    UPC_A = 12
    UPC_E = 7
    EAN_8 = 8
    EAN_13 = 13


@dataclass(kw_only=True, slots=True, eq=True)
class Barcode:
    code: int
    type: BarcodeType

    def __post_init__(self):
        # validate Barcode
        if not isinstance(self.code, int):
            raise ValueError("code must be an integer")
        if not isinstance(self.type, BarcodeType):
            raise ValueError("type must be an instance of BarcodeType")
        if len(str(self.code)) != self.type.value:
            raise ValueError(
                f"code must be {self.type.value} digits long, got {len(str(self.code))}"
            )
        if not validate_upc(self.code):
            raise ValueError("invalid barcode")
        
    def __repr__(self):
        return str(self.code)


def validate_upc(code) -> bool:
    digits = str(code)
    try:
        code = int(digits[-1])
        check = generate_checkdigit(int(digits[:-1]))
        return code == check

    except ValueError:
        return False
    
    except IndexError:
        return False


def generate_checkdigit(code: int) -> int:
    digits = [int(d) for d in str(code)]
    for i in range(0, len(digits), 2):
        digits[i] *= 3
    checkdigit = (10 - (sum(digits) % 10)) % 10

    return checkdigit
