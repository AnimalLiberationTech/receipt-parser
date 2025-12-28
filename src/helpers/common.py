import cloudscraper
import os
import random
from curl_cffi import requests
from itertools import groupby

IMPERSONATED_BROWSER = "chrome120"

def get_templates_dir() -> str:
    return os.path.join("src", "static", "templates")


def get_template_path(template_name: str) -> str:
    return os.path.join(get_templates_dir(), template_name)


def split_list(lst, delimiter) -> list[list]:
    return [
        list(group) for key, group in groupby(lst, lambda x: x == delimiter) if not key
    ]


def get_proxies(logger) -> list[str]:
    proxies = []
    sources = [
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
    ]
    
    for source in sources:
        try:
            resp = requests.get(source, timeout=3)
            if resp.status_code == 200:
                lines = resp.text.strip().split("\n")
                proxies.extend([line.strip() for line in lines if ":" in line])
        except Exception as e:
            logger.warning(f"Failed to fetch proxies from {source}: {e}")

    if proxies:
        # Remove duplicates and pick random ones
        proxies = list(set(proxies))
        return random.sample(proxies, min(len(proxies), 5))
    return []


def get_html(url: str, logger) -> str | None:
    try:
        resp = requests.get(
            url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"},
            timeout=10
        )

        if resp.status_code == 200:
            return resp.text
        logger.warning("GET %s response_code=%s", url, resp.status_code)
    except Exception as e:
        logger.warning("GET %s failed: %s", url, e)

    # Only set language, let curl_cffi handle the rest to match the fingerprint
    extra_headers = {
        "Accept-Language": "ro-MD,ro;q=0.9,en-US;q=0.8,en;q=0.7,ru;q=0.6",
    }

    try:
        # Use curl_cffi to bypass Cloudflare
        session = requests.Session(impersonate=IMPERSONATED_BROWSER)
        session.headers.update(extra_headers)

        # Visit root first to establish session/cookies
        try:
            session.get("https://mev.sfs.md/", timeout=5)
            # Update referer for the next request
            session.headers["Referer"] = "https://mev.sfs.md/"
        except Exception:
            pass

        resp = session.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.text
        logger.warning("curl_cffi GET %s impersonate=%s response_code=%s", url, IMPERSONATED_BROWSER, resp.status_code)
    except Exception as e:
        logger.error("curl_cffi GET %s impersonate=%s %s", url, IMPERSONATED_BROWSER, e)

    # Fallback to cloudscraper
    try:
        scraper = cloudscraper.create_scraper()
        resp = scraper.get(url, headers=extra_headers, timeout=10)
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
            session = requests.Session(impersonate=IMPERSONATED_BROWSER)
            session.proxies = {"http": proxy_url, "https": proxy_url}
            session.headers.update(extra_headers)
            
            resp = session.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.text
            logger.warning("proxy %s GET %s response_code=%s", proxy, url, resp.status_code)
        except Exception as e:
            logger.warning("proxy %s GET %s failed: %s", proxy, url, e)

    # Try Apify as last resort
    apify_api_key = os.environ.get("APIFY_API_KEY")
    if apify_api_key:
        try:
            proxy_url = f"http://auto:{apify_api_key}@proxy.apify.com:8000"
            session = requests.Session(impersonate=IMPERSONATED_BROWSER)
            session.proxies = {"http": proxy_url, "https": proxy_url}
            session.headers.update(extra_headers)

            resp = session.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.text
            logger.warning("Apify GET %s response_code=%s", url, resp.status_code)
        except Exception as e:
            logger.error("Apify GET %s error: %s", url, e)

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
