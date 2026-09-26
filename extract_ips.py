import requests
import json
import re
from bs4 import BeautifulSoup

TARGET_URL = "https://ashtemobile.tututweak.com/ii.html"
OUTPUT_FILE = "ashteips.json"

def fetch_and_extract():
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    print(f"Fetching content from {TARGET_URL}...")
    extracted_apps = []

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # گەڕیان دوای هەموو لینکەکانی ناو پەڕەکە کە بۆ پەڕەی یارییەکان دەچن
        cards = soup.find_all(['div', 'a', 'li'], class_=re.compile(r'(app|item|card|game|download)', re.I))
        if not cards:
            cards = soup.find_all('a', href=True)

        seen_links = set()

        for idx, card in enumerate(cards):
            name = ""
            page_url = ""

            if card.name == 'a':
                page_url = card.get('href', '')
                name = card.get_text(strip=True)
            else:
                link_tag = card.find('a', href=True)
                if link_tag:
                    page_url = link_tag.get('href', '')
                
                title_tag = card.find(['h1', 'h2', 'h3', 'h4', 'span', 'p'], class_=re.compile(r'(title|name)', re.I))
                if title_tag:
                    name = title_tag.get_text(strip=True)
                else:
                    name = card.get_text(strip=True)

            if not page_url or not name or len(name) < 2:
                continue
            
            if page_url.startswith('/'):
                page_url = "https://ashtemobile.tututweak.com" + page_url
            elif not page_url.startswith('http'):
                continue

            if page_url in seen_links:
                continue
            seen_links.add(page_url)

            # وەرگرتنی ئایکۆن
            icon = "https://ashtemobile.site/logo.png"
            img_tag = card.find('img') if card.name != 'a' else card.find('img')
            if img_tag and img_tag.get('src'):
                img_src = img_tag.get('src')
                if img_src.startswith('/'):
                    icon = "https://ashtemobile.tututweak.com" + img_src
                elif img_src.startswith('http'):
                    icon = img_src

            # ئێستا سەردانیکردنی پەڕەی تاکی یارییەکە بۆ دەرهێنانی لینکێ "Click to copy" (API Link)
            click_to_copy_url = page_url
            print(f"Checking details for: {name}...")
            try:
                sub_res = requests.get(page_url, headers=headers, timeout=10)
                # گەڕیان بەدوای لینکێ API یێ کە ?ref= تێدایە (لێنکێ Click to copy)
                match = re.search(r'(https://check0ver\.net/api/check0ver/[^"\'\s]+\.ipa\?ref=[A-Za-z0-9+/=]+)', sub_res.text)
                if match:
                    click_to_copy_url = match.group(1).replace('\\/', '/')
                else:
                    # گەڕیان لەناو input یا attribute کان ئەگەر Regex نەیتۆنی
                    sub_soup = BeautifulSoup(sub_res.text, 'html.parser')
                    inputs = sub_soup.find_all('input', type='text')
                    for inp in inputs:
                        val = inp.get('value', '')
                        if 'check0ver.net/api/' in val:
                            click_to_copy_url = val
                            break
            except Exception as e:
                print(f"  -> Error fetching subpage for {name}: {e}")

            extracted_apps.append({
                "id": str(99000000 + len(extracted_apps)),
                "name": name[:50],
                "version": "1.0",
                "size": "N/A",
                "icon": icon,
                "install_url": click_to_copy_url,   # لێرەدا لێنکێ کلیک تو کۆپی بڕێوەچوو
                "download_url": click_to_copy_url, # لێرەداش هەروەها
                "developerName": "AshteMobile",
                "localizedDescription": f"Extracted Click to Copy API link for: {name}"
            })

    except Exception as e:
        print(f"Error fetching target page: {e}")

    # تۆمارکردنا زانیاریان بۆ ناو فایلا ashteips.json
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(extracted_apps, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully generated {OUTPUT_FILE} with {len(extracted_apps)} apps containing Click-to-Copy API links.")

if __name__ == "__main__":
    fetch_and_extract()
