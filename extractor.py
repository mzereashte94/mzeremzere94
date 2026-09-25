import json
from datetime import datetime

print("=== ASHTE MOBILE: FULL APPS SOURCE GENERATOR ===")

json_file = "ashtemobile94.json"

# لێرەدا یارییەکانت زیاد بکە بە زانیارییە ڕاستەقینەکانەوە
apps_data = [
    {
        "name": "Block Blast!",
        "slug": "block-blast",
        "bundleIdentifier": "com.blockpuzzle", # لە وێنەکەتدا ئەمە بوو
        "version": "7.4.8", # وەشانی یارییەکە
        "size": 89044582, # قەبارە بە بایت (84.92 MB)
        "downloadURL": "لێرەدا_لینکی_ڕاستەقینەی_داونلۆدی_یارییەکە_دابنێ" 
    },
    {
        "name": "Check0ver App 1",
        "slug": "check0ver-app-1",
        "bundleIdentifier": "com.ashtemobile.check0ver-app-1",
        "version": "1.0",
        "size": 314572800,
        "downloadURL": "https://check0ver.net/api/check0ver/E669C4F905734AED2E9E/166810/0de72f5207d159483e527280fc5e530f.ipa?ref=d256S2NINnZKK2pVZ1l4KzBsTndUd0NSZUd6cGVFMFYvczZOWmJJRmdZcStNWWFyTkpRYkxqRWk4UFdyRXkrbkFBL0QzeXU3Rk9sbkYvSkdKT3E3aUxVa2szcTFGTW8yVzd2YnVhdiswdGZ3QkF0cXJNVmVpekpRMnV6ZWczVDAzWUEwckhDVmhnMWpHTjVLVVV3RmFUUUx4Z0JkcFRTVzdReGZrQlR3MFUzNG0xV09LTGx4QjA5eElNaGRremhK"
    }
]

apps_list = []
for app in apps_data:
    name = app["name"]
    slug = app["slug"]
    download_url = app["downloadURL"]
    bundle_id = app.get("bundleIdentifier", f"com.ashtemobile.{slug}")
    version = app.get("version", "1.0")
    app_size = app.get("size", 314572800)
    current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    
    apps_list.append({
        "name": name,
        "bundleIdentifier": bundle_id,
        "developerName": "AshteMobile",
        "version": version,
        "versionDate": current_time,
        "versionDescription": "Direct CDN Link",
        "downloadURL": download_url,
        "localizedDescription": f"Original CDN Link for {name}",
        "iconURL": "https://ashtemobile.site/logo.png",
        "tintColor": "#04ecfc",
        "size": app_size,
        "versions": [
            {
                "version": "1.0", # زۆرجار سۆرسەکان پێویستیان بە وەشانی بنەڕەتی هەیە
                "date": current_time,
                "localizedDescription": "Initial release",
                "downloadURL": download_url,
                "size": app_size,
                "minOSVersion": "14.0"
            }
        ]
    })

source_structure = {
    "name": "Ashtemobile",
    "identifier": "com.ashtemobile.source", 
    "subtitle": "Ksign & Feather Source",
    "description": "Full Catalog with Direct CDN Links.",
    "iconURL": "https://ashtemobile.site/logo.png",
    "website": "https://ashtemobile.site/",
    "tintColor": "#ff007f",
    "apps": apps_list,
    "news": []
}

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(source_structure, f, ensure_ascii=False, indent=4)

print(f"SUCCESS! Saved {len(apps_list)} apps to {json_file}")
