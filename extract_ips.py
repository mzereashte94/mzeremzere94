import requests
import json
import re

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

        # لێگه‌ڕیان بۆ لێنكێن JSON یێن شاراوه‌ د ناڤ ماڵپه‌ری دا
        json_urls = re.findall(r'https?://[^\s"\']+\.json', html_content)
        
        # ئه‌گه‌ر سۆرسه‌كێ JSON ل سه‌ر ماڵپه‌ری هه‌بت دێ زانیاریان ژێ كێشێت
        for j_url in set(json_urls):
            try:
                res = requests.get(j_url, headers=headers, timeout=10)
                res.encoding = 'utf-8'
                data = res.json()
                items = data if isinstance(data, list) else data.get('apps', data.get('items', data.get('games', [])))
                
                for idx, item in enumerate(items):
                    name = item.get('name') or item.get('title')
                    if not name or "باركرندا" in name:
                        continue
                    
                    extracted_apps.append({
                        "id": str(item.get('id', 99000000 + idx)),
                        "name": name,
                        "version": item.get('version', '1.0'),
                        "size": item.get('size', 'N/A'),
                        "icon": item.get('icon') or item.get('iconURL') or "https://ashtemobile.site/logo.png",
                        "install_url": item.get('install_url') or item.get('download_url') or item.get('downloadUrl') or "",
                        "download_url": item.get('download_url') or item.get('install_url') or item.get('downloadUrl') or "",
                        "developerName": "AshteMobile",
                        "localizedDescription": f"Auto extracted: {name}"
                    })
            except Exception as e:
                print(f"Error parsing inner JSON {j_url}: {e}")

    except Exception as e:
        print(f"Error fetching target page: {e}")

    # تۆماركرنا زانیاریان ب ئه‌نكدۆدكرنا دروست یا UTF-8
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(extracted_apps, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully generated {OUTPUT_FILE} with {len(extracted_apps)} apps.")

if __name__ == "__main__":
    fetch_and_extract()
