import logging
import re
from typing import Tuple

import requests
from OSMPythonTools.nominatim import Nominatim

OSM_HOST = "https://www.openstreetmap.org"

logger = logging.getLogger(__name__)

_nominatim = Nominatim()


def get_osm_id(osm_type: str, osm_key: str) -> str:
    return f"{osm_type[0].upper()}{osm_key}"


def lookup_osm_data(osm_type: str, osm_id: str) -> dict:
    osm_id_str = get_osm_id(osm_type, osm_id)
    try:
        result = _nominatim.query(osm_id_str, lookup=True)
        if result and len(result) > 0:
            elem = result[0]
            return {
                "place_id": elem.placeId(),
                "osm_type": elem.type(),
                "osm_id": elem.id(),
                "display_name": elem.displayName(),
                "lat": elem.lat(),
                "lon": elem.lon(),
                "address": elem.address(),
                "extratags": elem.tag("extratags") if elem.tag("extratags") else {},
            }
    except (AttributeError, IndexError, KeyError, TypeError) as e:
        # OSM object doesn't exist or has unexpected structure
        logger.warning("OSM lookup failed for %s: %s", osm_id_str, e)
    except requests.exceptions.RequestException as e:
        logger.warning("OSM network request failed for %s: %s", osm_id_str, e)
    return {}


def validate_osm_url(url: str) -> bool:
    """Validate that a URL is an OpenStreetMap URL."""
    return url.startswith(OSM_HOST)


def parse_osm_url(url: str) -> Tuple[str, str]:
    """Parse an OSM URL and extract the type and ID."""
    pattern = r"https://www.openstreetmap.org/(.*?)/(\d+)"
    match = re.search(pattern, url)
    if match:
        osm_type, osm_id = match.groups()
        return osm_type, osm_id

    raise ValueError("Invalid OSM URL")
