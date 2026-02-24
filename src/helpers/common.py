import hashlib
import os
from itertools import groupby

import requests

from src.schemas.common import OsmType, OsmTypeCode


def get_templates_dir() -> str:
    return os.path.join("src", "static", "templates")


def get_template_path(template_name: str) -> str:
    return os.path.join(get_templates_dir(), template_name)


def split_list(lst, delimiter) -> list[list]:
    return [
        list(group) for key, group in groupby(lst, lambda x: x == delimiter) if not key
    ]


def get_html(url: str, logger) -> str | None:
    try:
        resp = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
                "Accept-Language": "ro-MD,ro;q=0.9,en-US;q=0.8,en;q=0.7,ru;q=0.6",
            },
            timeout=5,
        )

        if resp.status_code == 200:
            return resp.text
        logger.warning("GET %s response_code=%s", url, resp.status_code)
    except requests.RequestException as e:
        logger.warning("GET %s failed: %s", url, e)

    try:
        api_user = os.environ.get("OXYLABS_API_USER")
        api_pass = os.environ.get("OXYLABS_API_PASS")

        if not (api_user and api_pass):
            logger.warning("missing OXYLABS_API_USER and OXYLABS_API_PASS")
            return None

        resp = requests.request(
            "POST",
            "https://realtime.oxylabs.io/v1/queries",
            auth=(api_user, api_pass),
            json={"source": "universal", "url": url},
            timeout=60,
        )

        if resp.status_code == 200:
            return resp.json()["results"][0]["content"]
        logger.warning("oxylabs %s response_code=%s", url, resp.status_code)
    except (requests.RequestException, ValueError, KeyError, IndexError) as e:
        logger.warning("oxylabs %s failed: %s", url, e)

    return None


def validate_barcode(barcode: str) -> bool:
    if not barcode.isdigit() or len(barcode) not in (8, 12, 13, 14):
        return False

    total = 0
    for i, num in enumerate(barcode[:-1]):
        multiplier = (i + 1) % 2 if len(barcode) == 14 else i % 2
        total += int(num) * (1 + (2 * multiplier))

    return str((10 - (total % 10)) % 10) == barcode[-1]


def is_localhost() -> bool:
    for local_ip in ["127.0.0.1", "localhost"]:
        if os.environ["WEBSITE_HOSTNAME"].startswith(local_ip):
            return True
    return False


def make_hash(url: str) -> str:
    return hashlib.md5(url.strip().encode("utf-8")).hexdigest()


def osm_type_to_code(osm_type: OsmType | str) -> OsmTypeCode:
    if not isinstance(osm_type, OsmType):
        osm_type = OsmType(osm_type)
    return OsmTypeCode[osm_type.name]
