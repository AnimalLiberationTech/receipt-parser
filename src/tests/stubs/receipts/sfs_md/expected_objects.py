from datetime import datetime
from uuid import UUID

from src.schemas.common import CountryCode, CurrencyCode, Unit
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
            unit=Unit.LITER,
            unit_quantity=1.0,
            price=14.13,
        ),
        PurchasedItem(
            name="ANGROMIX-77 Lapte din soia 1l",
            quantity=1.0,
            unit=Unit.LITER,
            unit_quantity=1.0,
            price=14.13,
        ),
        PurchasedItem(
            name="Guacamole Mediterraneo, 200 g, buc",
            quantity=2.0,
            unit=Unit.GRAM,
            unit_quantity=200.0,
            price=19.95,
        ),
        PurchasedItem(
            name="Guacamole Carribe, 200 g, buc",
            quantity=1.0,
            unit=Unit.GRAM,
            unit_quantity=200.0,
            price=19.95,
        ),
        PurchasedItem(
            name="MEGGLE Crema din branza Mascarpone 250g",
            quantity=1.0,
            unit=Unit.GRAM,
            unit_quantity=250.0,
            price=29.93,
        ),
    ],
)

LIN_RECEIPT_2 = SfsMdReceipt(
    id=None,
    date=datetime(2026, 1, 3, 18, 33, 16),
    user_id=UUID(USER_ID_1),
    company_id="1010600022460",
    company_name="MOLDRETAIL GROUP S.R.L.",
    country_code=CountryCode.MOLDOVA,
    shop_address="mun. Chisinau bd. Banulescu Bodoni, 57",
    cash_register_id="J403001576",
    key=668558,
    currency_code=CurrencyCode.MOLDOVAN_LEU,
    total_amount=101.8,
    receipt_url="https://mev.sfs.md/receipt-verifier/J403001576/101.8/668558/2026-01-03",
    purchases=[
        PurchasedItem(
            name="7 SPICE Tort BONAPARTE 1kg",
            quantity=1.0,
            unit=Unit.KILOGRAM,
            unit_quantity=1.0,
            price=82.0,
        ),
        PurchasedItem(
            name="GLORIA NUTS Seminte de floarea soarelui",
            quantity=2.0,
            price=9.9,
        ),
    ],
)

NANU_RECEIPT = SfsMdReceipt(
    id=None,
    date=datetime(2025, 8, 2, 17, 11, 3),
    user_id=UUID(USER_ID_1),
    company_id="1006600052073",
    company_name='"NANU MARKET" S.R.L.',
    country_code=CountryCode.MOLDOVA,
    shop_address="mun. Chisinau str. Constructorilor, 1",
    cash_register_id="J406003734",
    key=183608,
    currency_code=CurrencyCode.MOLDOVAN_LEU,
    total_amount=851.9,
    receipt_url="https://mev.sfs.md/receipt-verifier/J406003734/851.9/183608/2025-08-02",
    purchases=[
        PurchasedItem(
            name="5184 Colier din plastic cu surub si diblu pentru tevi canal",
            quantity=6.0,
            price=8.1,
        ),
        PurchasedItem(
            name="5100 Dop PP pentru canalizare, O50, sur, Aquer",
            quantity=2.0,
            price=4.05,
        ),
        PurchasedItem(
            name="5117 Cot PP pentru canalizare, O50/90?, sur, Aquer",
            quantity=2.0,
            price=8.1,
        ),
        PurchasedItem(
            name="5144 Teu PP pentru canalizare, O50е50/90?, sur, Aquer",
            quantity=2.0,
            price=18.0,
        ),
        PurchasedItem(
            name="6144 Colier din plastic O110, RTP",
            quantity=10.0,
            price=5.0,
        ),
        PurchasedItem(
            name="5120 Cot PP pentru canalizare, O110/45?, sur, Aquer",
            quantity=2.0,
            price=20.7,
        ),
        PurchasedItem(
            name="5121 Cot PP pentru canalizare, O110/90?, sur, Aquer",
            quantity=1.0,
            price=22.5,
        ),
        PurchasedItem(
            name="5116 Cot PP pentru canalizare, O50/45?, sur, Aquer",
            quantity=1.0,
            price=8.1,
        ),
        PurchasedItem(
            name="5148 Teu PP pentru canalizare, O110е50/90?, sur, Turplast-B",
            quantity=1.0,
            price=24.3,
        ),
        PurchasedItem(
            name="5312 Teu PP pentru canalizare, O110е50/67?, sur, Turplast-B",
            quantity=1.0,
            price=27.0,
        ),
        PurchasedItem(
            name="5115 Cot PP pentru canalizare, O110x50/90?, drept, sur, Tur",
            quantity=1.0,
            price=40.5,
        ),
        PurchasedItem(
            name="5159 Teava PVC pentru canalizare, SN2, O50е1,8x2000mm, gri,",
            quantity=3.0,
            price=37.8,
        ),
        PurchasedItem(
            name="5543 Teava PVC pentru canalizare, SN2, O110x2,2x3000mm, gri",
            quantity=2.0,
            price=125.1,
        ),
        PurchasedItem(
            name="5542 Teava PVC pentru canalizare, SN2, O110x2,2x2000mm, gri",
            quantity=2.0,
            price=82.8,
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
            unit=Unit.GRAM,
            unit_quantity=250.0,
            price=16.54,
        ),
        PurchasedItem(
            name="PAINE WELTMEISTE750G",
            quantity=1.0,
            unit=Unit.GRAM,
            unit_quantity=750.0,
            price=28.95,
        ),
        PurchasedItem(
            name="GUT.VARZA.MURAT.400G",
            quantity=1.0,
            unit=Unit.GRAM,
            unit_quantity=400.0,
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
