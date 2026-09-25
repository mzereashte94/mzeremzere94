import json
from datetime import datetime

print("=== ASHTE MOBILE: FULL APPS SOURCE GENERATOR ===")

json_file = "ashtemobile94.json"

# لێرەدا دەتوانیت هەموু ئەو یارییانە دابنێیت کە دەتەوێت لە سۆرسەکەتدا هەبن
# (نموونەی چەند یارییەک کە لینکی ڕاستەقینەیان هەیە)
apps_data = [
    {
        "name": "Check0ver App 1",
        "slug": "check0ver-app-1",
        "downloadURL": "https://check0ver.net/api/check0ver/E669C4F905734AED2E9E/166810/0de72f5207d159483e527280fc5e530f.ipa?ref=d256S2NINnZKK2pVZ1l4KzBsTndUd0NSZUd6cGVFMFYvczZOWmJJRmdZcStNWWFyTkpRYkxqRWk4UFdyRXkrbkFBL0QzeXU3Rk9sbkYvSkdKT3E3aUxVa2szcTFGTW8yVzd2YnVhdiswdGZ3QkF0cXJNVmVpekpRMnV6ZWczVDAzWUEwckhDVmhnMWpHTjVLVVV3RmFUUUx4Z0JkcFRTVzdReGZrQlR3MFUzNG0xV09LTGx4QjA5eElNaGRremhK"
    },
    # دەتوانیت یارییەکانی تریش لێرە زیاد بکەیت بە هەمان شێوە:
    # {
    #     "name": "ناوی یاری",
    #     "slug": "nav-i-yari",
    #     "downloadURL": "لینکە ڕاستەقینەکەی ref=..."
    # }
]

apps_list = []
for app in apps_data:
    name = app["name"]
    slug = app["slug"]
    download_url = app["downloadURL"]
    
    apps_list.append({
        "name": name,
        "bundleIdentifier": f"com.ashtemobile.{slug}",
        "developerName": "AshteMobile",
        "version": "1.0",
        "versionDate": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "versionDescription": "Direct CDN Link",
        "downloadURL": download_url,
        "localizedDescription": f"Original CDN Link for {name}",
        "iconURL": "https://ashtemobile.site/logo.png",
        "tintColor": "#04ecfc",
        "size": 314572800,
        "versions": [
            {
                "version": "1.0",
                "date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                "localizedDescription": "Initial release",
                "downloadURL": download_url,
                "size": 314572800,
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
