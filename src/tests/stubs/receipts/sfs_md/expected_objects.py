from datetime import datetime
from uuid import UUID

from src.schemas.common import CountryCode, CurrencyCode
from src.schemas.purchased_item import PurchasedItem
from src.schemas.sfs_md.receipt import SfsMdReceipt
from src.tests import USER_ID_1

LIN_RECEIPT = SfsMdReceipt(
    id=None,
    date=datetime(2024, 1, 17, 14, 58, 22),
    user_id=UUID(USER_ID_1),
    company_id="1010600022460",
    company_name="MOLDRETAIL GROUP S.R.L.",
    country_code=CountryCode.MOLDOVA,
    shop_address="mun. Chisinau bd. Banulescu Bodoni, 57",
    cash_register_id="J403001576",
    key=135932,
    currency_code=CurrencyCode.MOLDOVAN_LEU,
    total_amount=118.04,
    receipt_url="https://mev.sfs.md/receipt-verifier/J403001576/118.04/135932/2024-01-17",
    purchases=[
        PurchasedItem(
            name="ANGROMIX-77 Lapte din soia 1l",
            quantity=1.0,
            price=14.13,
        ),
        PurchasedItem(
            name="ANGROMIX-77 Lapte din soia 1l",
            quantity=1.0,
            price=14.13,
        ),
        PurchasedItem(
            name="Guacamole Mediterraneo, 200 g, buc",
            quantity=2.0,
            price=19.95,
        ),
        PurchasedItem(
            name="Guacamole Carribe, 200 g, buc",
            quantity=1.0,
            price=19.95,
        ),
        PurchasedItem(
            name="MEGGLE Crema din branza Mascarpone " "250g",
            quantity=1.0,
            price=29.93,
        ),
    ],
)

KL_RECEIPT = SfsMdReceipt(
    id=None,
    date=datetime(2023, 10, 17, 19, 54, 18),
    user_id=UUID(USER_ID_1),
    company_id="1016600004811",
    company_name="KAUFLAND S.R.L.",
    country_code=CountryCode.MOLDOVA,
    shop_address="mun Chisinau str Kiev 7",
    cash_register_id="J702003194",
    key=25312,
    currency_code=CurrencyCode.MOLDOVAN_LEU,
    total_amount=370.85,
    receipt_url="https://mev.sfs.md/receipt-verifier/J702003194/370.85/25312/2023-10-17",
    purchases=[
        PurchasedItem(
            name="VDR SALAM BISC.250G",
            quantity=1.0,
            price=16.54,
        ),
        PurchasedItem(
            name="PAINE WELTMEISTE750G",
            quantity=1.0,
            price=28.95,
        ),
        PurchasedItem(
            name="GUT.VARZA.MURAT.400G",
            quantity=1.0,
            price=16.9,
        ),
        PurchasedItem(
            name="K-VEGGIE IAURT VANIL",
            quantity=1.0,
            price=35.0,
        ),
        PurchasedItem(
            name="K-VEGGIE IAURT SOIA",
            quantity=6.0,
            price=35.0,
        ),
        PurchasedItem(name="BANANE", quantity=1.322, price=28.3),
        PurchasedItem(
            name="STRUGURI ALBI",
            quantity=2.444,
            price=27.7,
        ),
        PurchasedItem(
            name="PERE SMARIA BUTEIR",
            quantity=0.288,
            price=39.9,
        ),
        PurchasedItem(name="VINETE", quantity=0.672, price=12.3),
        PurchasedItem(
            name="DOVLECEI",
            quantity=0.704,
            price=14.9,
        ),
    ],
)
