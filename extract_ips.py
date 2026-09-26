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
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching page: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    extracted_apps = []

    # Search all app elements
    items = soup.find_all(['div', 'a', 'li'], class_=re.compile(r'app|item|card|game|box', re.I)) or soup.find_all('a')

    for idx, item in enumerate(items):
        title_el = item.find(['h1', 'h2', 'h3', 'h4', 'span', 'p'], class_=re.compile(r'title|name', re.I)) or item
        title = title_el.get_text(strip=True) if title_el else ""

        if not title or len(title) < 2 or title.lower() in ['home', 'get', 'download', 'vip', 'menu', 'close']:
            continue

        img_el = item.find('img')
        icon = img_el.get('src', '') if img_el else ""
        if icon and not icon.startswith('http'):
            icon = "https://ashtemobile.tututweak.com/" + icon.lstrip('/')

        link_el = item if item.name == 'a' else item.find('a', href=True)
        download_url = ""
        if link_el:
            href = link_el.get('href', '')
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                if href.startswith('http') or href.startswith('itms-services'):
                    download_url = href
                else:
                    download_url = "https://ashtemobile.tututweak.com/" + href.lstrip('/')

        meta_text = item.get_text()
        size_match = re.search(r'\d+(\.\d+)?\s*(MB|GB)', meta_text, re.I)
        version_match = re.search(r'v?\d+\.\d+(\.\d+)?', meta_text, re.I)

        size = size_match.group(0) if size_match else "N/A"
        version = version_match.group(0) if version_match else "1.0"

        if download_url or icon:
            extracted_apps.append({
                "id": str(99000000 + idx),
                "name": title,
                "version": version,
                "size": size,
                "icon": icon or "https://ashtemobile.site/logo.png",
                "install_url": download_url,
                "download_url": download_url,
                "developerName": "AshteMobile",
                "localizedDescription": f"Auto extracted from AshteMobile store: {title}"
            })

    if extracted_apps:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(extracted_apps, f, ensure_ascii=False, indent=2)
        print(f"Successfully updated {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_and_extract()
