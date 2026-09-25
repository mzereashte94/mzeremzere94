import json
import requests
from datetime import datetime

print("=== ASHTE MOBILE: AUTO IPA EXTRACTOR ===")

json_file = "ashtemobile94.json"
base_url = "https://check0ver.net/en/iapps"
api_url = "https://check0ver.net/api/iapps/{}/download"

# بەکارهێنانی هێدەری Inertia بۆ ئەوەی ڕاستەوخۆ JSON وەربگرین و سێرڤەرەکە بلۆکمان نەکات
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "X-Inertia": "true",
    "X-Inertia-Version": "mimusoft-ipa-check0ver-customer-1.0.0"
}

apps_list = []

try:
    print("Fetching data from website...")
    # هێنانی داتاکان
    response = requests.get(base_url, headers=headers, timeout=15)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        page_data = response.json()
        
        # دەرهێنانی یارییەکان ڕاستەوخۆ لە JSON
        games = page_data.get("props", {}).get("paginator", {}).get("data", [])
        print(f"Found {len(games)} games.")
        
        for game in games:
            uuid = game.get("uuid")
            name = game.get("name")
            version = game.get("version", "1.0")
            bundle_id = game.get("bundle", f"com.ashtemobile.{uuid}")
            icon = game.get("image", "https://ashtemobile.site/logo.png")
            desc = game.get("description", "Auto extracted app")
            
            # هێنانی لینکی داونلۆدی ڕاستەقینە
            dl_link = f"https://check0ver.net/en/iapps/{uuid}"
            try:
                dl_response = requests.get(api_url.format(uuid), headers=headers, allow_redirects=False, timeout=10)
                if dl_response.status_code in [301, 302, 303, 307, 308]:
                    dl_link = dl_response.headers.get("Location", dl_link)
                elif dl_response.status_code == 200:
                    dl_json = dl_response.json()
                    dl_link = dl_json.get("url", dl_json.get("download_url", dl_link))
            except Exception as e:
                print(f"Error getting link for {name}: {e}")
            
            print(f"Added: {name}")
            current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
            
            apps_list.append({
                "name": name,
                "bundleIdentifier": bundle_id,
                "developerName": "CheckOver",
                "version": version,
                "versionDate": current_time,
                "versionDescription": "Auto Extracted",
                "downloadURL": dl_link,
                "localizedDescription": desc,
                "iconURL": icon,
                "tintColor": "#04ecfc",
                "size": 314572800,
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
        print(f"Failed to fetch page. Server returned: {response.text[:200]}")
        
except Exception as e:
    print(f"Fatal error: {e}")

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

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(source_structure, f, ensure_ascii=False, indent=4)

print(f"\nSUCCESS! Saved {len(apps_list)} apps.")
