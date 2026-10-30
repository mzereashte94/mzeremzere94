#!/usr/bin/env python3
"""
IPA link extractor for JavaScript-rendered pages.

Sources (default): the AshteMobile store and https://check0ver.net/en/iapps
Install:  pip install selenium webdriver-manager requests
Run:      python ashte_scraper.py --max-wait 40 --retries 3
"""
import argparse
import json
import logging
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

DEFAULT_URLS = [
    "https://ashtemobile.tututweak.com/o.html",
    "https://check0ver.net/en/iapps",
]

URL_RE = re.compile(r"https?://[^\s\"'<>\\]+", re.I)
IPA_RE = re.compile(r"\.ipa\b", re.I)
CHECK_RE = re.compile(r"check0ver\.net/api/check0ver/", re.I)
PLIST_RE = re.compile(r"\.plist\b", re.I)
NAME_KEYS = ("name", "title", "app_name", "appName", "label")

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
HTTP_HEADERS = {"User-Agent": UA, "Accept": "*/*"}

# Every attribute value containing a URL, plus nearby text (used for app names)
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

# Clicks a visible "Load more" style button (returns true if it clicked one)
LOAD_MORE_JS = """
const re = /^(load more|show more|view more|more|next)$/i;
const el = Array.from(document.querySelectorAll('button, [role=button]'))
  .find(e => re.test((e.innerText || '').trim()) && e.offsetParent !== null && !e.disabled);
if (el) { el.click(); return true; }
return false;
"""

log = logging.getLogger("scraper")


# ---------------------------------------------------------------- helpers
def is_target(url: str) -> bool:
    return bool(IPA_RE.search(url) or CHECK_RE.search(url))


def is_direct_ipa(url: str) -> bool:
    """A real .ipa link, not a check0ver wrapper."""
    return bool(IPA_RE.search(url)) and not CHECK_RE.search(url)


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


def walk_json(obj, base_url: str, name_hint: str | None = None):
    """Yield (link, name) for every .ipa / check0ver link anywhere in a JSON tree."""
    if isinstance(obj, dict):
        name = next(
            (
                obj[k].strip()
                for k in NAME_KEYS
                if isinstance(obj.get(k), str) and obj[k].strip()
            ),
            name_hint,
        )
        for v in obj.values():
            yield from walk_json(v, base_url, name)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_json(v, base_url, name_hint)
    elif isinstance(obj, str):
        links = extract_links(obj)
        if (
            not links
            and IPA_RE.search(obj)
            and " " not in obj
            and len(obj) < 500
            and not obj.lower().startswith(("http", "itms"))
        ):
            links = [urljoin(base_url, obj.strip())]  # relative path like /files/a.ipa
        for link in links:
            yield link, name_hint


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


def click_load_more(driver, max_rounds: int = 20) -> None:
    for _ in range(max_rounds):
        if not driver.execute_script(LOAD_MORE_JS):
            return
        time.sleep(1.5)
        scroll_until_stable(driver, 6, 2)


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


def inspect_network(driver):
    """Scan browser traffic. Returns ([(link, name)], [api response summaries])."""
    found: list[tuple[str, str | None]] = []
    seen: dict[tuple, dict] = {}
    try:
        logs = driver.get_log("performance")
    except WebDriverException:
        return found, []
    for entry in logs:
        try:
            msg = json.loads(entry["message"])["message"]
        except (ValueError, KeyError):
            continue
        method, params = msg.get("method"), msg.get("params", {})
        if method == "Network.requestWillBeSent":
            req_url = params.get("request", {}).get("url", "")
            found += [(u, None) for u in extract_links(req_url)]
        elif method == "Network.responseReceived":
            rtype = params.get("type")
            if rtype not in ("XHR", "Fetch", "Script"):
                continue
            resp = params.get("response", {})
            try:
                body = driver.execute_cdp_cmd(
                    "Network.getResponseBody", {"requestId": params["requestId"]}
                )
            except WebDriverException:
                continue
            if body.get("base64Encoded"):
                continue
            text = body.get("body", "")
            if rtype != "Script":
                key = (resp.get("url"), resp.get("status"))
                seen[key] = {
                    "url": resp.get("url"),
                    "status": resp.get("status"),
                    "mime": resp.get("mimeType"),
                    "size": len(text),
                    "preview": text[:300],
                }
            try:
                found += list(walk_json(json.loads(text), resp.get("url", "")))
            except ValueError:
                found += [(u, None) for u in extract_links(text)]
    summaries = sorted(seen.values(), key=lambda d: d["url"] or "")
    return found, summaries


# ---------------------------------------------------------------- scraping
def scrape_page(driver, url: str, args, results: dict) -> dict:
    log.info("Opening %s", url)
    before = len(results)
    driver.get(url)
    WebDriverWait(driver, args.max_wait).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    scroll_until_stable(driver, args.max_wait, args.stable)
    click_load_more(driver)

    def add(link: str, via: str, page: str, name: str | None = None) -> None:
        e = results.setdefault(
            link, {"name": name or name_from_url(link), "page": page, "via": set()}
        )
        e["via"].add(via)
        if name and e["name"] == name_from_url(link):  # replace placeholder name
            e["name"] = name

    # 1) DOM attributes (+ iframes): best source of names on normal pages
    for item in collect_dom(driver):
        for link in extract_links(item["value"]):
            add(link, "dom", url, pick_name(item, link))

    # 2) raw page source
    for link in extract_links(driver.page_source):
        add(link, "source", url)

    # 3) network traffic: API/JSON responses used by single-page apps
    net_links, api_summaries = inspect_network(driver)
    for link, name in net_links:
        add(link, "network", url, name)

    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text[:1500]
    except WebDriverException:
        page_text = ""

    found_here = len(results) - before
    log.info("%s -> %d new links, %d API responses seen", url, found_here, len(api_summaries))
    return {"new_links": found_here, "api_responses": api_summaries, "page_text": page_text}


def scrape(args):
    driver = build_driver(not args.no_headless)
    results: dict[str, dict] = {}
    debug: dict[str, dict] = {}
    try:
        for url in args.url:
            try:
                debug[url] = scrape_page(driver, url, args, results)
            except WebDriverException as e:
                log.error("Failed on %s: %s", url, str(e).splitlines()[0])
                debug[url] = {"error": str(e).splitlines()[0]}
    finally:
        driver.quit()

    apps = [
        {
            "id": i,
            "name": e["name"],
            "type": "check0ver" if CHECK_RE.search(link) else "ipa",
            "page": e["page"],
            "download_url": link,
            "found_via": sorted(e["via"]),
        }
        for i, (link, e) in enumerate(results.items(), start=1)
    ]
    return apps, debug


# ---------------------------------------------------------------- resolving
def read_text(resp, limit: int = 1_000_000) -> str:
    data, size = [], 0
    for chunk in resp.iter_content(65536):
        data.append(chunk)
        size += len(chunk)
        if size >= limit:
            break
    return b"".join(data).decode(resp.encoding or "utf-8", errors="ignore")


def resolve_link(url: str, referer: str, depth: int = 0) -> str | None:
    """Follow redirects / JSON / plist wrappers until the original .ipa URL is found."""
    if is_direct_ipa(url):
        return url
    if depth > 4:
        return None

    headers = {**HTTP_HEADERS, "Referer": referer}
    try:
        resp = requests.get(
            url, headers=headers, stream=True, timeout=25, allow_redirects=True
        )
    except requests.RequestException as e:
        log.warning("Could not open %s (%s)", url, e.__class__.__name__)
        return None

    try:
        # 1) the redirect chain passes through / ends at the .ipa
        for r in [*resp.history, resp]:
            for cand in (urljoin(r.url, r.headers.get("Location", "")), r.url):
                if cand and is_direct_ipa(cand):
                    return cand

        # 2) the final response is the file download itself
        ctype = resp.headers.get("Content-Type", "").lower()
        disp = resp.headers.get("Content-Disposition", "").lower()
        if "octet-stream" in ctype or ".ipa" in disp:
            return resp.url

        # 3) a wrapper page / JSON: look inside the body
        text = read_text(resp)
        links = extract_links(text)
        for link in links:
            if is_direct_ipa(link):
                return link
        for link in links:  # another check0ver link nested inside
            if link != url:
                found = resolve_link(link, referer, depth + 1)
                if found:
                    return found

        # 4) itms-services manifest (.plist) that contains the .ipa URL
        for m in URL_RE.findall(clean(text)):
            m = m.rstrip(".,;:)]}")
            if PLIST_RE.search(m):
                try:
                    pr = requests.get(m, headers=headers, timeout=20)
                except requests.RequestException:
                    continue
                for link in extract_links(pr.text):
                    if is_direct_ipa(link):
                        return link

        log.warning(
            "Unresolved %s -> HTTP %s, %s, body starts: %r",
            url, resp.status_code, ctype or "?", text[:200],
        )
        return None
    finally:
        resp.close()


def resolve_apps(apps: list[dict], referer: str, workers: int = 8):
    """Replace check0ver links with the original .ipa links."""
    todo = [a["download_url"] for a in apps if a["type"] == "check0ver"]
    resolved: dict[str, str | None] = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(resolve_link, u, referer): u for u in todo}
        for fut in as_completed(futs):
            try:
                resolved[futs[fut]] = fut.result()
            except Exception as e:  # one bad link must not kill the run
                log.warning("Resolve error for %s: %s", futs[fut], e)
                resolved[futs[fut]] = None

    final: dict[str, dict] = {}
    unresolved: list[dict] = []
    for a in apps:
        src = a["download_url"] if a["type"] == "check0ver" else None
        direct = resolved.get(src) if src else a["download_url"]
        if not direct:
            unresolved.append({"name": a["name"], "source_link": src})
            continue
        e = final.setdefault(
            direct,
            {
                "name": a["name"],
                "page": a.get("page"),
                "download_url": direct,
                "source_link": src,
                "found_via": set(),
            },
        )
        e["source_link"] = e["source_link"] or src
        e["found_via"].update(a["found_via"])

    out = []
    for i, e in enumerate(final.values(), start=1):
        e["found_via"] = sorted(e["found_via"])
        out.append({"id": i, **e})
    return out, unresolved


# ---------------------------------------------------------------- main
def parse_args():
    p = argparse.ArgumentParser(description="Extract IPA links from dynamic pages")
    p.add_argument("--url", action="append", help="page to scrape (repeatable)")
    p.add_argument("--out", default="ashteips.json")
    p.add_argument("--debug-file", default="debug_network.json")
    p.add_argument("--no-debug", dest="debug", action="store_false")
    p.add_argument("--max-wait", type=float, default=30, help="max seconds to wait")
    p.add_argument("--stable", type=float, default=4, help="seconds of no change = loaded")
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--no-headless", action="store_true", help="show the browser window")
    p.add_argument("--no-resolve", action="store_true", help="keep check0ver links as they are")
    p.add_argument("--workers", type=int, default=8, help="parallel link resolvers")
    args = p.parse_args()
    args.url = args.url or DEFAULT_URLS
    return args


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()

    apps: list[dict] = []
    debug: dict = {}
    for attempt in range(1, args.retries + 1):
        try:
            apps, debug = scrape(args)
        except WebDriverException as e:
            log.error("Attempt %d failed: %s", attempt, str(e).splitlines()[0])
        if apps:
            break
        log.warning("Attempt %d/%d found nothing.", attempt, args.retries)
        time.sleep(2 * attempt)

    if args.debug and debug:
        # deterministic content (no timestamps) so git only sees real changes
        Path(args.debug_file).write_text(
            json.dumps(debug, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        log.info("Saved debug info to %s", args.debug_file)

    unresolved: list[dict] = []
    if apps and not args.no_resolve:
        log.info("Resolving %d links to the original .ipa source...", len(apps))
        apps, unresolved = resolve_apps(apps, args.url[0], args.workers)
        log.info("Resolved: %d, unresolved: %d", len(apps), len(unresolved))

    if not apps:
        log.error("No links found; leaving %s untouched.", args.out)
        return 1

    output = {
        "sources": args.url,
        "total_links_found": len(apps),
        "apps": apps,
        "unresolved": unresolved,
    }
    Path(args.out).write_text(
        json.dumps(output, ensure_ascii=False, indent=4), encoding="utf-8"
    )
    log.info("Done: %d links saved to %s", len(apps), args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
