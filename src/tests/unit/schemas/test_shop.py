from unittest import TestCase
from uuid import UUID

from pydantic_core._pydantic_core import ValidationError  # noqa

from src.schemas.common import CountryCode, OsmType
from src.schemas.osm_data import OsmData
from src.schemas.shop import Shop


class TestShop(TestCase):
    def setUp(self):
        self.osm_data = OsmData(type=OsmType.NODE, key=123, lat="7.0", lon="28.0")

    def test_auto_generated_fields(self):
        shop = Shop(
            country_code=CountryCode.MOLDOVA,
            company_id="company_id",
            shop_address="shop_address",
            osm_data=self.osm_data,
        )
        self.assertIsInstance(shop.id, UUID)

    def test_wrong_types(self):
        with self.assertRaises(ValidationError) as ctx:
            Shop(
                id="not_uuid",
                country_code="md",
                company_id="company_id",
                shop_address="shop_address",
                osm_data=self.osm_data,
            )
        errors = ctx.exception.errors()
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]["loc"], ("id",))
        self.assertEqual(errors[0]["msg"], "Input should be an instance of UUID")
        self.assertEqual(errors[1]["loc"], ("country_code",))
        self.assertEqual(errors[1]["msg"], "Input should be an instance of CountryCode")
