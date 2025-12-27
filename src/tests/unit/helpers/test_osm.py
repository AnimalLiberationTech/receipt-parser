from unittest import TestCase
from unittest.mock import patch

from src.helpers.osm import get_osm_id, lookup_osm_object, validate_osm_url, parse_osm_url


class TestOsm(TestCase):
    def test_get_osm_id(self):
        self.assertEqual(get_osm_id("node", "123"), "N123")
        self.assertEqual(get_osm_id("way", "456"), "W456")
        self.assertEqual(get_osm_id("relation", "789"), "R789")

    @patch("requests.get")
    def test_lookup_osm_object(self, mock_get):
        mock_get.return_value.json.return_value = [{"key": "value"}]
        self.assertEqual(lookup_osm_object("node", "123"), {"key": "value"})
        mock_get.return_value.json.return_value = []
        self.assertEqual(lookup_osm_object("node", "123"), {})

    def test_validate_osm_url(self):
        self.assertTrue(validate_osm_url("https://www.openstreetmap.org/node/123"))
        self.assertFalse(validate_osm_url("https://www.example.com/node/123"))

    def test_parse_osm_url(self):
        self.assertEqual(
            parse_osm_url("https://www.openstreetmap.org/node/123"), ("node", "123")
        )
        with self.assertRaises(ValueError):
            parse_osm_url("https://www.example.com/node/123")
