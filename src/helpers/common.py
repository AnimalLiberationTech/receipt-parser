import os
import cloudscraper
from curl_cffi import requests
from itertools import groupby


def get_templates_dir() -> str:
    return os.path.join("src", "static", "templates")


def get_template_path(template_name: str) -> str:
    return os.path.join(get_templates_dir(), template_name)


def split_list(lst, delimiter) -> list[list]:
    return [
        list(group) for key, group in groupby(lst, lambda x: x == delimiter) if not key
    ]


def get_html(url: str, logger) -> str | None:
    # Common headers to mimic a real browser
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9,ro;q=0.8,ru;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Referer": "https://mev.sfs.md/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

    # Try different impersonations to bypass protections
    impersonations = ["chrome120", "safari15_3", "chrome"]
    
    # First try with curl_cffi
    for imp in impersonations:
        try:
            # Use curl_cffi to bypass Cloudflare
            resp = requests.get(url, impersonate=imp, headers=headers, timeout=30)
            if resp.status_code == 200:
                return resp.text
            logger.warning("curl_cffi GET %s impersonate=%s response_code=%s", url, imp, resp.status_code)
        except Exception as e:
            logger.error("curl_cffi GET %s impersonate=%s %s", url, imp, e)

    # Fallback to cloudscraper
    try:
        scraper = cloudscraper.create_scraper()
        resp = scraper.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.text
        logger.warning("cloudscraper GET %s response_code=%s", url, resp.status_code)
    except Exception as e:
        logger.error("cloudscraper GET %s %s", url, e)
            
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
