import cloudscraper
import json
from bs4 import BeautifulSoup

TARGET_URL = "https://check0ver.net/en"
OUTPUT_FILE = "ashteips.json"

def fetch_and_extract():
    scraper = cloudscraper.create_scraper()
    extracted_apps = []

    print(f"Connecting to {TARGET_URL}...")
    try:
        response = scraper.get(TARGET_URL, timeout=30)
        print(f"Response Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to fetch page. Status: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        app_div = soup.find('div', id='app')
        
        if app_div and app_div.has_attr('data-page'):
            page_data = json.loads(app_div['data-page'])
            apps_list = page_data.get('props', {}).get('paginator', {}).get('data', [])
            print(f"Total apps found in JSON data: {len(apps_list)}")
            
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
        else:
            print("Error: 'app' div with 'data-page' not found in HTML!")
            # لێرەدا دەبینین ئایا ماڵپەڕەکە کۆدێکی تر یان کۆدێ کلاودفلێر دەرخستووە
            print("Page snippet:", response.text[:200])

    except Exception as e:
        print(f"Exception occurred: {e}")

    # پاراستن د ناو فایلی دا
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(extracted_apps, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(extracted_apps)} apps to {OUTPUT_FILE}.")

if __name__ == "__main__":
    fetch_and_extract()
