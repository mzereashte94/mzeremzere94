#!/usr/bin/env python3
"""
Robust IPA / check0ver link extractor.

Install:  pip install selenium webdriver-manager
Run:      python ashte_scraper.py --max-wait 40 --retries 3
"""
import argparse
import json
import logging
import re
import sys
import time
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlparse

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

DEFAULT_URL = "https://ashtemobile.tututweak.com/o.html"

URL_RE = re.compile(r"https?://[^\s\"'<>\\]+", re.I)
IPA_RE = re.compile(r"\.ipa\b", re.I)
CHECK_RE = re.compile(r"check0ver\.net/api/check0ver/", re.I)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Collects every attribute value containing a URL, plus nearby text (for app names)
DOM_JS = """
const out = [];
document.querySelectorAll('*').forEach(el => {
  for (const a of el.attributes) {
    if (a.value && a.value.indexOf('http') !== -1) {
      const card = el.closest('li, article, tr, [class*=card], [class*=item], [class*=app]');
      out.push({
        value: a.value,
        text: (el.getAttribute('title') || el.getAttribute('aria-label') || el.innerText || '').slice(0, 200),
        card: card ? (card.innerText || '').slice(0, 300) : ''
      });
    }
  }
});
return out;
"""

log = logging.getLogger("scraper")


# ---------------------------------------------------------------- helpers
def is_target(url: str) -> bool:
    return bool(IPA_RE.search(url) or CHECK_RE.search(url))


def clean(text: str) -> str:
    text = unescape(text)
    return (
        text.replace("\\/", "/")
        .replace("\\u0026", "&")
        .replace("\\u003d", "=")
        .replace("\\u003D", "=")
    )


def extract_links(text: str) -> list[str]:
    if not text:
        return []
    links = (m.rstrip(".,;:)]}") for m in URL_RE.findall(clean(text)))
    return [u for u in links if is_target(u)]


def name_from_url(url: str) -> str:
    base = Path(unquote(urlparse(url).path)).name
    return base or urlparse(url).netloc


def pick_name(item: dict, url: str) -> str:
    skip = ("http", "download", "get", "install")
    for text in (item.get("text", ""), item.get("card", "")):
        for line in text.splitlines():
            line = line.strip()
            if 2 <= len(line) <= 80 and not line.lower().startswith(skip):
                return line
    return name_from_url(url)


# ---------------------------------------------------------------- browser
def build_driver(headless: bool) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1366,3000")
    opts.add_argument(f"--user-agent={UA}")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    # record network traffic so API (XHR/fetch) responses can be scanned too
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    try:  # Selenium Manager (built in to selenium >= 4.6)
        return webdriver.Chrome(options=opts)
    except WebDriverException:
        from webdriver_manager.chrome import ChromeDriverManager

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=opts)


def scroll_until_stable(driver, max_wait: float, stable_for: float) -> None:
    """Scroll down and wait until the page stops changing (lazy loading)."""
    end = time.time() + max_wait
    last_sig, last_change = None, time.time()
    while time.time() < end:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.8)
        sig = driver.execute_script(
            "return [document.body.scrollHeight, document.body.innerHTML.length].join(':')"
        )
        if sig != last_sig:
            last_sig, last_change = sig, time.time()
        elif time.time() - last_change >= stable_for:
            return
    log.warning("Page never fully stabilised; continuing with what loaded.")


def collect_dom(driver) -> list[dict]:
    items = list(driver.execute_script(DOM_JS))
    for i in range(len(driver.find_elements(By.TAG_NAME, "iframe"))):
        try:
            driver.switch_to.frame(i)
            items += driver.execute_script(DOM_JS)
        except WebDriverException:
            pass
        finally:
            driver.switch_to.default_content()
    return items


def links_from_network(driver) -> list[str]:
    found: list[str] = []
    try:
        logs = driver.get_log("performance")
    except WebDriverException:
        return found
    for entry in logs:
        try:
            msg = json.loads(entry["message"])["message"]
        except (ValueError, KeyError):
            continue
        method, params = msg.get("method"), msg.get("params", {})
        if method == "Network.requestWillBeSent":
            found += extract_links(params.get("request", {}).get("url", ""))
        elif method == "Network.responseReceived" and params.get("type") in (
            "XHR",
            "Fetch",
            "Script",
        ):
            try:
                body = driver.execute_cdp_cmd(
                    "Network.getResponseBody", {"requestId": params["requestId"]}
                )
                found += extract_links(body.get("body", ""))
            except WebDriverException:
                pass
    return found


# ---------------------------------------------------------------- scraping
def scrape(args) -> list[dict]:
    driver = build_driver(not args.no_headless)
    try:
        log.info("Opening %s", args.url)
        driver.get(args.url)
        WebDriverWait(driver, args.max_wait).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        scroll_until_stable(driver, args.max_wait, args.stable)

        results: dict[str, dict] = {}

        def add(link: str, via: str, name: str | None = None) -> None:
            e = results.setdefault(
                link, {"name": name or name_from_url(link), "via": set()}
            )
            e["via"].add(via)

        # 1) DOM attributes (+ iframes), gives the best names
        for item in collect_dom(driver):
            for link in extract_links(item["value"]):
                add(link, "dom", pick_name(item, link))

        # 2) raw page source
        for link in extract_links(driver.page_source):
            add(link, "source")

        # 3) network traffic (API responses)
        for link in links_from_network(driver):
            add(link, "network")

        if not results and args.debug:
            Path("debug_page.html").write_text(driver.page_source, encoding="utf-8")
            log.info("No links found; saved debug_page.html for inspection.")

        return [
            {
                "id": i,
                "name": e["name"],
                "type": "check0ver" if CHECK_RE.search(link) else "ipa",
                "download_url": link,
                "found_via": sorted(e["via"]),
            }
            for i, (link, e) in enumerate(results.items(), start=1)
        ]
    finally:
        driver.quit()


def parse_args():
    p = argparse.ArgumentParser(description="Extract IPA links from a dynamic page")
    p.add_argument("--url", default=DEFAULT_URL)
    p.add_argument("--out", default="ashteips.json")
    p.add_argument("--max-wait", type=float, default=30, help="max seconds to wait")
    p.add_argument("--stable", type=float, default=4, help="seconds of no change = loaded")
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--no-headless", action="store_true", help="show the browser window")
    p.add_argument("--debug", action="store_true", default=True)
    return p.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()

    apps: list[dict] = []
    for attempt in range(1, args.retries + 1):
        try:
            apps = scrape(args)
        except WebDriverException as e:
            log.error("Attempt %d failed: %s", attempt, str(e).splitlines()[0])
        if apps:
            break
        log.warning("Attempt %d/%d found nothing.", attempt, args.retries)
        time.sleep(2 * attempt)

    if not apps:
        log.error("No links found; leaving %s untouched.", args.out)
        return 1

    output = {
        "source_website": args.url,
        "total_links_found": len(apps),
        "apps": apps,
    }
    Path(args.out).write_text(
        json.dumps(output, ensure_ascii=False, indent=4), encoding="utf-8"
    )
    log.info("Done: %d links saved to %s", len(apps), args.out)
    return 0 if apps else 1


if __name__ == "__main__":
    sys.exit(main())
