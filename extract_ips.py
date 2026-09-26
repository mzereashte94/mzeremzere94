import requests
from bs4 import BeautifulSoup
import json
import re

TARGET_URL = "https://ashtemobile.tututweak.com/ii.html"
OUTPUT_FILE = "ashteips.json"

def fetch_and_extract():
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    }
    
    print(f"Fetching content from {TARGET_URL}...")
    extracted_apps = []

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # هێنانی هەموو بلۆکەکان یان لینکەکانی ناو لاپەڕەکە
        all_links = soup.find_all('a', href=True)
        
        # ئەگەر کارت یان دیڤ هەبوو
        containers = soup.find_all(['div', 'li', 'article'])
        
        items = containers if len(containers) > 0 else all_links

        for idx, item in enumerate(items):
            # دۆزینەوەی ناونیشان
            title = ""
            title_el = item.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'p', 'b', 'strong'])
            if title_el:
                title = title_el.get_text(strip=True)
            elif item.name == 'a':
                title = item.get_text(strip=True)

            if not title or len(title) < 2 or title.lower() in ['home', 'get', 'download', 'vip', 'menu', 'close', 'back', 'top']:
                continue

            # دۆزینەوەی ئایکۆن
            img_el = item.find('img')
            icon = ""
            if img_el:
                icon = img_el.get('src') or img_el.get('data-src') or ""
                if icon and not icon.startswith('http'):
                    icon = "https://ashtemobile.tututweak.com/" + icon.lstrip('/')

            # دۆزینەوەی لینکی داگرتن
            link_el = item if item.name == 'a' else item.find('a', href=True)
            download_url = ""
            if link_el:
                href = link_el.get('href', '')
                if href and not href.startswith('#') and not href.startswith('javascript:'):
                    if href.startswith('http') or href.startswith('itms-services'):
                        download_url = href
                    else:
                        download_url = "https://ashtemobile.tututweak.com/" + href.lstrip('/')

            if download_url or icon or len(title) > 3:
                extracted_apps.append({
                    "id": str(99000000 + idx),
                    "name": title,
                    "version": "1.0",
                    "size": "N/A",
                    "icon": icon or "https://ashtemobile.site/logo.png",
                    "install_url": download_url,
                    "download_url": download_url,
                    "developerName": "AshteMobile",
                    "localizedDescription": f"Auto extracted: {title}"
                })

    except Exception as e:
        print(f"Error fetching page: {e}")

    # لابردنی بڕگەی دووبارە
    unique_apps = []
    seen_names = set()
    for app in extracted_apps:
        if app["name"] not in seen_names:
            seen_names.add(app["name"])
            unique_apps.append(app)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(unique_apps, f, ensure_ascii=False, indent=2)
    
    print(f"File {OUTPUT_FILE} created with {len(unique_apps)} apps.")

if __name__ == "__main__":
    fetch_and_extract()
