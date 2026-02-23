from unittest import TestCase
from uuid import UUID

from pydantic_core._pydantic_core import ValidationError  # noqa

from src.schemas.common import CountryCode, OsmType
from src.schemas.osm_data import OsmData
from src.schemas.shop import Shop


class TestShop(TestCase):
    def setUp(self):
        self.osm_data = OsmData(type=OsmType.NODE, key=123, lat="7.0", lon="28.0")
        self.creator_user_id = UUID("123e4567-e89b-12d3-a456-426614174000")

    def test_auto_generated_fields(self):
        shop = Shop(
            country_code=CountryCode.MOLDOVA,
            company_id="company_id",
            address="shop_address",
            osm_data=self.osm_data,
            creator_user_id=self.creator_user_id,
        )
        self.assertIsNone(shop.id)
        self.assertIsInstance(shop.creation_time, int)
        self.assertIsNotNone(shop.osm_id)
        self.assertTrue(shop.osm_id.startswith("1:"))  # NODE type code is 1

    def test_osm_id_generation(self):
        shop = Shop(
            country_code=CountryCode.MOLDOVA,
            company_id="company_id",
            address="shop_address",
            osm_data=self.osm_data,
            creator_user_id=self.creator_user_id,
        )
        self.assertEqual(shop.osm_id, "1:123")

    def test_wrong_types(self):
        with self.assertRaises(ValidationError) as ctx:
            Shop(
                country_code="invalid_country",
                company_id="company_id",
                address="shop_address",
                osm_data=self.osm_data,
                creator_user_id="not_uuid",
            )
        errors = ctx.exception.errors()
        self.assertEqual(len(errors), 2)
        error_locs = {error["loc"][0] for error in errors}
        self.assertIn("country_code", error_locs)
        self.assertIn("creator_user_id", error_locs)

    def test_missing_required_creator_user_id(self):
        with self.assertRaises(ValidationError) as ctx:
            Shop(
                country_code=CountryCode.MOLDOVA,
                company_id="company_id",
                address="shop_address",
                osm_data=self.osm_data,
            )
        errors = ctx.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["loc"], ("creator_user_id",))
        self.assertEqual(errors[0]["type"], "missing")
