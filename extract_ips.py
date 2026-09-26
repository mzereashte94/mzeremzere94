import cloudscraper
import json
from bs4 import BeautifulSoup

TARGET_URL = "https://check0ver.net/en"
OUTPUT_FILE = "ashteips.json"

def fetch_and_extract():
    # بەکارهێنانی cloudscraper بۆ تێپەڕاندنی پاراستنا ماڵپەری
    scraper = cloudscraper.create_scraper()
    print(f"Fetching content from {TARGET_URL} using cloudscraper...")
    extracted_apps = []

    try:
        response = scraper.get(TARGET_URL, timeout=20)
        response.encoding = 'utf-8'
        print(f"Status Code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        app_div = soup.find('div', id='app')
        
        if app_div and app_div.has_attr('data-page'):
            try:
                page_data = json.loads(app_div['data-page'])
                apps_list = page_data.get('props', {}).get('paginator', {}).get('data', [])
                print(f"Found {len(apps_list)} apps in page data.")
                
                for idx, app in enumerate(apps_list):
                    name = app.get('name', 'Unknown')
                    uuid = app.get('uuid', '')
                    
                    download_url = f"https://check0ver.net/api/check0ver/{uuid}.ipa" if uuid else ""
                    
                    extracted_apps.append({
                        "id": str(88000000 + idx),
                        "name": name,
                        "version": app.get('version', '1.0'),
                        "size": app.get('size', 'N/A'),
                        "icon": app.get('image', 'https://ashtemobile.site/logo.png'),
                        "install_url": download_url,
                        "download_url": download_url,
                        "developerName": "AshteMobile",
                        "localizedDescription": f"Extracted via API for {name}"
                    })
            except Exception as e:
                print(f"Error parsing JSON data: {e}")
        else:
            print("Could not find data-page attribute in HTML.")
            print(response.text[:300])

    except Exception as e:
        print(f"Error fetching target page: {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(extracted_apps, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully generated {OUTPUT_FILE} with {len(extracted_apps)} apps.")

if __name__ == "__main__":
    fetch_and_extract()
