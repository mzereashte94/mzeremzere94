import json
import requests

def fetch_all_apps():
    # بەکارهێنانی APIی ڕاستەوخۆی check0ver بۆ هێنانی هەموو یاری و ئەپەکان
    api_url = "https://check0ver.net/api/check0ver/apps"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
        "Accept": "application/json"
    }

    apps_list = []

    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # ئەگەر زانیارییەکان لە ناو لیستی data یان apps بێت
            raw_apps = data if isinstance(data, list) else data.get("apps", [])

            for item in raw_apps:
                download_link = item.get("download_url") or item.get("downloadURL") or item.get("install_url", "")
                
                app_entry = {
                    "id": item.get("id", 142653783),
                    "name": item.get("name", "Unknown Game"),
                    "version": item.get("version", "1.0.0"),
                    "size": item.get("size", "200 MB"),
                    "icon": item.get("icon", "https://ashtemobile.site/logo.png"),
                    "badge": "",
                    "type": "games",
                    "install_url": download_link,
                    "download_url": download_link,
                    "bundleIdentifier": item.get("bundleIdentifier") or item.get("bundle_id") or "com.ashtemobile.app",
                    "developerName": "AshteMobile",
                    "subtitle": item.get("subtitle", "Modded App"),
                    "localizedDescription": "Downloaded from AshteMobile",
                    "iconURL": item.get("iconURL") or item.get("icon") or "https://ashtemobile.site/logo.png",
                    "tintColor": "#04ecfc",
                    "category": "games",
                    "screenshots": [],
                    "versions": [
                        {
                            "version": item.get("version", "1.0.0"),
                            "date": "2026-09-26T14:43:39.000000Z",
                            "localizedDescription": None,
                            "downloadURL": download_link,
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
                apps_list.append(app_entry)
        else:
            print(f"API returned status code: {response.status_code}")

    except Exception as e:
        print(f"Error fetching from API: {e}")

    return apps_list

def generate_ashteipa():
    all_apps = fetch_all_apps()

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
        "apps": all_apps
    }

    with open('ashteipa.json', 'w', encoding='utf-8') as file:
        json.dump(json_structure, file, indent=2, ensure_ascii=False)

    print(f"Done! Successfully added {len(all_apps)} apps to ashteipa.json")

if __name__ == '__main__':
    generate_ashteipa()
