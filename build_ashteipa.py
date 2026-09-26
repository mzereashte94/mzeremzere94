import json

# لیستی ئەپ و یارییەکان
apps_data = [
    {
        "name": "Gardenscapes",
        "bundle_id": "com.playrix.gardenscapes",
        "download_url": "https://check0ver.net/api/check0ver/E669C4F905734AED2E9E/168185/f3e8ff826db015dcd4f6e94ace230bfb.ipa?ref=OUhPeHFXV1FBVE9wMUVVdWxGMG1lNHV0UlpZWGc0cXNoMWhxZitSd1kxUkZWWXE0enlTWCtCZlduTHNVT1kwT0ZFRkR6UkNRR2QxVkVFNUdnaHVIY25yZ2QvNzlGVHlQYTFBWUIxclRVYmxuL2FBNVRmak9Tbit5WUtkZEpneDh6NldYQVBoWXYyeHFjaW9ld0NBRTQ5RWF4cXFPS1JNaTdlVFFOaE9CMm15VXZyNHpIM2hQMXBTMW13Z0NkV0h2",
        "version": "9.9.5",
        "size": "196.36 MB"
    }
]

def generate_ashteipa():
    formatted_apps = []
    
    for item in apps_data:
        app_entry = {
            "id": 142653783,
            "name": item["name"],
            "version": item["version"],
            "size": item["size"],
            "icon": "https://ashtemobile.site/logo.png",
            "badge": "",
            "type": "games",
            "install_url": item["download_url"],
            "download_url": item["download_url"],
            "bundleIdentifier": item["bundle_id"],
            "developerName": "AshteMobile",
            "subtitle": "Modded App",
            "localizedDescription": "Downloaded from AshteMobile",
            "iconURL": "https://ashtemobile.site/logo.png",
            "tintColor": "#04ecfc",
            "category": "games",
            "screenshots": [],
            "versions": [
                {
                    "version": item["version"],
                    "date": "2026-09-26T14:43:39.000000Z",
                    "localizedDescription": None,
                    "downloadURL": item["download_url"],
                    "size": 200445788,
                    "buildVersion": None,
                    "minOSVersion": "14.0"
                }
            ],
            "appPermissions": {
                "entitlements": [],
                "privacy": {
                    "NSUserTrackingUsageDescription": ""
                }
            },
            "patreon": []
        }
        formatted_apps.append(app_entry)

    json_structure = {
        "name": "Ashtemobile",
        "subtitle": "A source for all of my apps & games",
        "description": "Welcome to my source!",
        "iconURL": "https://ashtemobile.site/logo.png",
        "website": "https://ashtemobile.site/",
        "patreonURL": "https://ashtemobile.site/Ashtemobile",
        "tintColor": "#ff007f",
        "featuredApps": [],
        "headerURL": "https://ashtemobile.site/logo.png",
        "apps": formatted_apps
    }

    # تەنها فایلی ashteipa.json نوێ دەکاتەوە
    with open('ashteipa.json', 'w', encoding='utf-8') as file:
        json.dump(json_structure, file, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    generate_ashteipa()
