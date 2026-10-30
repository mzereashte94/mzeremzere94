#!/usr/bin/env python3
"""
Lists every app on https://check0ver.net/en/iapps (and nothing else).

The site is an Inertia.js app: every HTML page already contains that page's
full data inside <div id="app" data-page="...">, so a plain HTTP request is
enough. No Chrome / Selenium is needed (use --browser only if requests get
blocked).

Install:  pip install requests
Run:      python ashte_scraper.py
Options:  --category <uuid>   only one category (repeatable)
          --browser            read pages with headless Chrome instead
"""
import argparse
import json
import logging
import re
import sys
import time
from html import unescape
from pathlib import Path
from urllib.parse import urlencode

import requests

BASE = "https://check0ver.net"
LIST_URL = f"{BASE}/en/iapps"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
DATA_PAGE_RE = re.compile(r'<div[^>]*\bid="app"[^>]*\bdata-page="([^"]*)"', re.I | re.S)

log = logging.getLogger("scraper")


# ---------------------------------------------------------------- parsing
def parse_data_page(html_text: str) -> dict:
    """Extract the Inertia page object from the HTML of a page."""
    m = DATA_PAGE_RE.search(html_text)
    if not m:
        raise ValueError("data-page not found (blocked, or the site layout changed)")
    return json.loads(unescape(m.group(1)))


def get_paginator(page: dict) -> dict:
    try:
        return page["props"]["paginator"]
    except (KeyError, TypeError):
        raise ValueError("page has no props.paginator (layout changed?)")


def normalise(item: dict) -> dict:
    uuid = item["uuid"]
    return {
        "uuid": uuid,
        "name": (item.get("name") or "").strip(),
        "bundle": item.get("bundle"),
        "version": item.get("version"),
        "size": item.get("size"),
        "icon": item.get("image"),
        "description": (item.get("description") or "").replace("\r\n", "\n").strip(),
        "updated_at": item.get("updatedAt"),
        "is_free": bool(item.get("isFree")),
        # only what the site itself exposes to a visitor; null when it doesn't
        "download_url": item.get("downloadURL"),
        "page_url": f"{BASE}/en/iapps/{uuid}",
    }


# ---------------------------------------------------------------- fetching
class HttpFetcher:
    def __init__(self, delay: float):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": UA, "Accept-Language": "en"})

    def page(self, params: dict) -> dict:
        r = self.session.get(LIST_URL, params=params, timeout=30)
        if r.status_code in (429, 503):
            ra = r.headers.get("Retry-After", "")
            time.sleep(min(int(ra) if ra.isdigit() else 10, 60))
        r.raise_for_status()
        page = parse_data_page(r.text)
        time.sleep(self.delay)  # be polite to the server
        return page

    def close(self) -> None:
        self.session.close()


class BrowserFetcher:
    """Fallback: read the same data-page attribute with headless Chrome."""

    def __init__(self, delay: float):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        self.delay = delay
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument(f"--user-agent={UA}")
        self.driver = webdriver.Chrome(options=opts)

    def page(self, params: dict) -> dict:
        from selenium.webdriver.support.ui import WebDriverWait

        self.driver.get(f"{LIST_URL}?{urlencode(params)}")
        js = "var a=document.getElementById('app'); return a ? a.getAttribute('data-page') : null;"
        raw = WebDriverWait(self.driver, 30).until(lambda d: d.execute_script(js))
        time.sleep(self.delay)
        return json.loads(raw)

    def close(self) -> None:
        self.driver.quit()


def get_page(fetcher, params: dict, attempts: int = 4) -> dict:
    for i in range(1, attempts + 1):
        try:
            return fetcher.page(params)
        except Exception as e:  # network, HTTP status, parsing, selenium
            log.warning("page %s attempt %d/%d failed: %s", params.get("page"), i, attempts, e)
            if i == attempts:
                raise
            time.sleep(min(5 * i, 30))


# ---------------------------------------------------------------- crawling
def crawl(fetcher, base_params: dict, max_pages: int = 0):
    first = get_page(fetcher, {**base_params, "page": 1})
    pag = get_paginator(first)
    last = pag["meta"]["last_page"]
    total = pag["meta"]["total"]
    if max_pages:
        last = min(last, max_pages)
    log.info("Site reports %d apps on %d pages", total, pag["meta"]["last_page"])

    items: dict[str, dict] = {}

    def take(page: dict) -> None:
        for it in get_paginator(page)["data"]:
            items.setdefault(it["uuid"], it)  # de-duplicate (the list can shift while crawling)

    take(first)
    failed: list[int] = []
    for n in range(2, last + 1):
        try:
            take(get_page(fetcher, {**base_params, "page": n}))
        except Exception as e:
            log.error("Giving up on page %d: %s", n, e)
            failed.append(n)
        if n % 20 == 0:
            log.info("... page %d/%d, %d apps so far", n, last, len(items))
    return items, failed, total


# ---------------------------------------------------------------- main
def parse_args():
    p = argparse.ArgumentParser(description="Collect the app list from check0ver.net/en/iapps")
    p.add_argument("--out", default="ashteips.json")
    p.add_argument("--category", action="append", help="category uuid to filter by (repeatable)")
    p.add_argument("--delay", type=float, default=0.6, help="seconds between requests")
    p.add_argument("--max-pages", type=int, default=0, help="stop after N pages (testing)")
    p.add_argument("--browser", action="store_true", help="use headless Chrome instead of requests")
    p.add_argument("--allow-partial", action="store_true", help="save even if some pages failed")
    return p.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()

    base_params = {f"filter[inCategories][{i}]": c for i, c in enumerate(args.category or [])}
    fetcher = BrowserFetcher(args.delay) if args.browser else HttpFetcher(args.delay)
    try:
        items, failed, total = crawl(fetcher, base_params, args.max_pages)
    except Exception as e:
        log.error("Could not read the first page: %s", e)
        if not args.browser:
            log.error("If the site blocks plain requests, try: --browser")
        return 1
    finally:
        fetcher.close()

    if failed and not args.allow_partial:
        log.error("%d page(s) failed %s; leaving %s untouched.", len(failed), failed[:10], args.out)
        return 1
    if not items:
        log.error("No apps found; leaving %s untouched.", args.out)
        return 1

    # stable order + no changing counters (downloads/views), so git only sees real changes
    apps = sorted(
        (normalise(it) for it in items.values()),
        key=lambda a: (a["name"].lower(), a["uuid"]),
    )
    output = {
        "source": LIST_URL,
        "categories": args.category or [],
        "total_apps": len(apps),
        "apps_with_download_url": sum(1 for a in apps if a["download_url"]),
        "apps": apps,
    }
    Path(args.out).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info(
        "Done: %d apps saved to %s (%d have a public download_url; site total %d)",
        len(apps), args.out, output["apps_with_download_url"], total,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
