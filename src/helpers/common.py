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


def get_proxies(logger) -> list[str]:
    try:
        # Fetch a list of free proxies
        resp = requests.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt", timeout=5)
        if resp.status_code == 200:
            proxies = resp.text.strip().split("\n")
            return proxies[:5]
    except Exception as e:
        logger.warning(f"Failed to fetch proxies: {e}")
    return []


def get_html(url: str, logger) -> str | None:
    # Common headers to mimic a real browser
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "ro-MD,ro;q=0.9,en-US;q=0.8,en;q=0.7,ru;q=0.6",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
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
            session = requests.Session(impersonate=imp)
            session.headers.update(headers)
            
            # Visit root first to establish session/cookies
            try:
                session.get("https://mev.sfs.md/", timeout=10)
                # Update referer for the next request
                session.headers["Referer"] = "https://mev.sfs.md/"
                session.headers["Sec-Fetch-Site"] = "same-origin"
            except Exception:
                pass

            resp = session.get(url, timeout=30)
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

    # Try with proxies if direct connection fails
    proxies = get_proxies(logger)
    for proxy in proxies:
        proxy_url = f"http://{proxy}"
        logger.info(f"Trying with proxy: {proxy_url}")
        
        try:
            # Use chrome120 with proxy
            session = requests.Session(impersonate="chrome120")
            session.proxies = {"http": proxy_url, "https": proxy_url}
            session.headers.update(headers)
            
            resp = session.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.text
            logger.warning("proxy %s GET %s response_code=%s", proxy, url, resp.status_code)
        except Exception as e:
            logger.warning("proxy %s GET %s failed: %s", proxy, url, e)
            
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
