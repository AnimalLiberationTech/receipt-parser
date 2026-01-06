from unittest import TestCase
from unittest.mock import patch, MagicMock

from src.helpers.osm import get_osm_id, lookup_osm_data, validate_osm_url, parse_osm_url


class TestOsm(TestCase):
    def test_get_osm_id(self):
        self.assertEqual(get_osm_id("node", "123"), "N123")
        self.assertEqual(get_osm_id("way", "456"), "W456")
        self.assertEqual(get_osm_id("relation", "789"), "R789")

    @patch("src.helpers.osm._nominatim")
    def test_lookup_osm_data(self, mock_nominatim):
        mock_elem = MagicMock()
        mock_elem.placeId.return_value = 12345
        mock_elem.type.return_value = "node"
        mock_elem.id.return_value = 123
        mock_elem.displayName.return_value = "Test Place"
        mock_elem.lat.return_value = "51.5074"
        mock_elem.lon.return_value = "0.1278"
        mock_elem.address.return_value = {"city": "London"}
        mock_elem.tag.return_value = None
        mock_nominatim.query.return_value = [mock_elem]

        result = lookup_osm_data("node", "123")
        self.assertEqual(result["place_id"], 12345)
        self.assertEqual(result["display_name"], "Test Place")

        # Test empty result
        mock_nominatim.query.return_value = []
        self.assertEqual(lookup_osm_data("node", "123"), {})

    def test_validate_osm_url(self):
        self.assertTrue(validate_osm_url("https://www.openstreetmap.org/node/123"))
        self.assertFalse(validate_osm_url("https://www.example.com/node/123"))

    def test_parse_osm_url(self):
        self.assertEqual(
            parse_osm_url("https://www.openstreetmap.org/node/123"), ("node", "123")
        )
        with self.assertRaises(ValueError):
            parse_osm_url("https://www.example.com/node/123")
