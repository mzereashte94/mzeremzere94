import json
import re
import html
import requests
from datetime import datetime

print("=== ASHTE MOBILE: AUTO IPA EXTRACTOR ===")

json_file = "ashtemobile94.json"
base_url = "https://check0ver.net"
# لینکی API کە بەرپرسە لە پێدانی لینکی ڕاستەقینەی IPA
api_url = "https://check0ver.net/api/iapps/{}/download"

# بەکارهێنانی هێدەری مۆبایل بۆ ئەوەی سایتەکە وا بزانێت لە مۆبایلەوە داواکارییەکە دەکرێت
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
    "Accept": "application/json"
}

session = requests.Session()
session.headers.update(headers)

apps_list = []

try:
    # 1. هێنانی پەڕەی سەرەکی یارییەکان
    print("Fetching main page...")
    response = session.get(f"{base_url}/en/iapps")
    
    # 2. دەرهێنانی داتاکان و یارییەکان لەناو کۆدی HTML
    match = re.search(r'data-page="([^"]+)"', response.text)
    if match:
        encoded_data = match.group(1)
        decoded_data = html.unescape(encoded_data)
        page_data = json.loads(decoded_data)
        
        # وەرگرتنی لیستی یارییەکان لەناو فایلە شاراوەکە
        games = page_data.get("props", {}).get("paginator", {}).get("data", [])
        print(f"Found {len(games)} games. Extracting direct IPA links...")
        
        for game in games:
            uuid = game.get("uuid")
            name = game.get("name")
            version = game.get("version", "1.0")
            bundle_id = game.get("bundle", f"com.ashtemobile.{uuid}")
            icon = game.get("image", "https://ashtemobile.site/logo.png")
            desc = game.get("description", "")
            
            # 3. پەیوەندیکردن بە API بۆ وەرگرتنی لینکی IPA
            dl_link = f"{base_url}/en/iapps/{uuid}" # لینکی یەدەگ ئەگەر نەدۆزرایەوە
            try:
                # داواکردنی لینکەکە بەبێ ڕیدایرێکت (بۆ گرتنی لینکی سێرڤەرەکە)
                dl_response = session.get(api_url.format(uuid), allow_redirects=False)
                
                if dl_response.status_code in [301, 302]:
                    dl_link = dl_response.headers.get("Location", dl_link)
                elif dl_response.status_code == 200:
                    dl_json = dl_response.json()
                    dl_link = dl_json.get("url", dl_json.get("download_url", dl_link))
            except Exception as e:
                print(f"Error getting link for {name}: {e}")
            
            print(f"Extracted -> {name}")
            
            current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
            
            # 4. خستنە ناو فۆرماتی تایبەت بە AltStore و Feather
            apps_list.append({
                "name": name,
                "bundleIdentifier": bundle_id,
                "developerName": "CheckOver",
                "version": version,
                "versionDate": current_time,
                "versionDescription": "Auto Extracted IPA Link",
                "downloadURL": dl_link,
                "localizedDescription": desc,
                "iconURL": icon,
                "tintColor": "#04ecfc",
                "size": 314572800, # قەبارەی بنەڕەتی
                "versions": [
                    {
                        "version": version,
                        "date": current_time,
                        "localizedDescription": "Latest release",
                        "downloadURL": dl_link,
                        "size": 314572800,
                        "minOSVersion": "14.0"
                    }
                ]
            })
    else:
        print("Could not find data in the website.")
        
except Exception as e:
    print(f"Fatal error: {e}")

# 5. دروستکردنی سۆرسی کۆتایی
source_structure = {
    "name": "Ashtemobile",
    "identifier": "com.ashtemobile.source", 
    "subtitle": "Ksign & Feather Source",
    "description": "Auto Generated Full Catalog with Direct Links.",
    "iconURL": "https://ashtemobile.site/logo.png",
    "website": "https://ashtemobile.site/",
    "tintColor": "#ff007f",
    "apps": apps_list,
    "news": []
}

# 6. پاشەکەوتکردنی لەناو فایلی JSON
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(source_structure, f, ensure_ascii=False, indent=4)

print(f"\nSUCCESS! Saved {len(apps_list)} apps with direct IPA links to {json_file}")
