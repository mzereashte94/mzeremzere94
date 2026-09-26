import requests
import json
import re
from bs4 import BeautifulSoup

# لێرەدا ڕاستەوخۆ لینکە سەرەکییەکەی check0ver دەکەینە ئامانج
TARGET_URL = "https://check0ver.net/en" # یان ئەو لینکەی کە لیستی یارییەکانی لێیە
OUTPUT_FILE = "ashteips.json"

def fetch_and_extract():
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://check0ver.net/"
    }
    
    print(f"Connecting to {TARGET_URL}...")
    extracted_apps = []

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        print(f"Status Code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # گەڕان بەدوای داتاکانی پەڕەکە (ئەگەر Inertia.js بێت یان HTML ی ئاسایی)
        app_div = soup.find('div', id='app')
        apps_list = []
        
        if app_div and app_div.has_attr('data-page'):
            try:
                page_data = json.loads(app_div['data-page'])
                apps_list = page_data.get('props', {}).get('paginator', {}).get('data', [])
                print(f"Found {len(apps_list)} apps via page data JSON.")
            except Exception as e:
                print(f"Error parsing page data JSON: {e}")

        # ئەگەر لەڕێگەی JSON نەدۆزراوەوە، بە شێوازی تگ و لینک دەگەڕێین
        if not apps_list:
            links = soup.find_all('a', href=re.compile(r'/iapps/'))
            print(f"Found {len(links)} app links directly from HTML.")
            
            seen_urls = set()
            for link in links:
                href = link.get('href')
                if href not in seen_urls:
                    seen_urls.add(href)
                    full_url = href if href.startswith('http') else "https://check0ver.net" + href
                    name = link.get_text(strip=True) or "Unknown App"
                    
                    apps_list.append({
                        "name": name,
                        "uuid": href.split('/')[-2] if len(href.split('/')) > 2 else "",
                        "version": "1.0",
                        "size": "N/A",
                        "image": "https://ashtemobile.site/logo.png",
                        "direct_page": full_url
                    })

        for idx, app in enumerate(apps_list):
            name = app.get('name', f'App {idx+1}')
            uuid = app.get('uuid')
            page_url = app.get('direct_page') or (f"https://check0ver.net/en/iapps/{uuid}/download" if uuid else "")
            
            if not page_url:
                continue

            print(f"Processing: {name}...")
            click_to_copy_url = page_url
            
            try:
                sub_res = requests.get(page_url, headers=headers, timeout=10)
                # گەڕیان بەدوای لینکێ API یێ کە ?ref= تێدایە (لینکەی Click to copy)
                match = re.search(r'(https://check0ver\.net/api/check0ver/[^"\'\s]+\.ipa\?ref=[A-Za-z0-9+/=]+)', sub_res.text)
                if match:
                    click_to_copy_url = match.group(1).replace('\\/', '/')
                    print(f"  -> Got Click-to-Copy API Link!")
                else:
                    # پشکنی لەناو input کان
                    sub_soup = BeautifulSoup(sub_res.text, 'html.parser')
                    for inp in sub_soup.find_all('input', type='text'):
                        val = inp.get('value', '')
                        if 'check0ver.net/api/' in val:
                            click_to_copy_url = val
                            break
            except Exception as e:
                print(f"  -> Error fetching subpage: {e}")

            extracted_apps.append({
                "id": str(88000000 + idx),
                "name": name,
                "version": app.get('version', '1.0'),
                "size": app.get('size', 'N/A'),
                "icon": app.get('image', 'https://ashtemobile.site/logo.png'),
                "install_url": click_to_copy_url,
                "download_url": click_to_copy_url,
                "developerName": "AshteMobile",
                "localizedDescription": f"Extracted from check0ver.net: {name}"
            })

    except Exception as e:
        print(f"Error fetching target page: {e}")

    # تۆمارکردنا زانیاریان بۆ ناو فایلا ashteips.json
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(extracted_apps, f, ensure_ascii=False, indent=2)
    
    print(f"\nSuccessfully generated {OUTPUT_FILE} with {len(extracted_apps)} apps.")

if __name__ == "__main__":
    fetch_and_extract()
