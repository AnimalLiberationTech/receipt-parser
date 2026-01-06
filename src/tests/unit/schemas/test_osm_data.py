from unittest import TestCase

from pydantic_core._pydantic_core import ValidationError  # noqa

from src.schemas.common import OsmType
from src.helpers.osm import get_osm_id
from src.schemas.osm_data import OsmData


class TestOsmData(TestCase):
    def test_init(self):
        osm_data = OsmData(
            type=OsmType.NODE,
            key=123,
            lat="51.5074",
            lon="0.1278",
        )
        self.assertEqual(osm_data.id, get_osm_id(OsmType.NODE, "123"))

    def test_wrong_types(self):
        with self.assertRaises(ValidationError) as ctx:
            OsmData(
                type="NODE",
                key=123,
                lat="51.5074",
                lon="0.1278",
            )
        errors = ctx.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["loc"], ("type",))
        self.assertEqual(errors[0]["msg"], "Input should be an instance of OsmType")

