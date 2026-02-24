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
        # Mock the element's toJSON() method to return a dict
        mock_json_elem = {"place_id": 12345, "lat": "51.5074", "lon": "0.1278"}

        # Mock the first result element
        mock_first_elem = MagicMock()
        mock_first_elem.toJSON.return_value = mock_json_elem

        # Mock the query result object
        mock_result = MagicMock()
        mock_result.firstResult.return_value = mock_first_elem
        mock_result.displayName.return_value = "Test Place"
        mock_result.address.return_value = {"city": "London"}

        mock_nominatim.query.return_value = mock_result

        result = lookup_osm_data("node", "123")
        self.assertEqual(result["place_id"], 12345)
        self.assertEqual(result["display_name"], "Test Place")

        # Test empty result - when query returns None or an object without firstResult
        mock_nominatim.query.return_value = None
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
