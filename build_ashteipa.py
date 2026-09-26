import json
import re
import requests
from bs4 import BeautifulSoup

def fetch_all_apps():
    url = "https://check0ver.net/"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching website: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    apps_list = []

    # استخراج تمام لینک‌ها و دکمه‌های دانلود از صفحه
    # در صورت وجود API مستقیم، می‌توانید آدرس API را جایگزین کنید
    for card in soup.find_all(['div', 'a'], class_=re.compile(r'card|item|app', re.I)):
        name_elem = card.find(['h2', 'h3', 'span', 'p'], class_=re.compile(r'title|name', re.I))
        link_elem = card.find('a', href=re.compile(r'\.ipa', re.I)) or card if card.name == 'a' else None
        
        if name_elem and link_elem and link_elem.get('href'):
            app_name = name_elem.text.strip()
            download_url = link_elem['href']
            
            # اصلاح لینک‌های نسبی به لینک کامل
            if not download_url.startswith('http'):
                download_url = f"https://check0ver.net{download_url}"

            app_entry = {
                "id": abs(hash(app_name)) % (10**9),
                "name": app_name,
                "version": "1.0.0",
                "size": "200 MB",
                "icon": "https://ashtemobile.site/logo.png",
                "badge": "",
                "type": "games",
                "install_url": download_url,
                "download_url": download_url,
                "bundleIdentifier": f"com.ashtemobile.{re.sub(r'\W+', '', app_name).lower()}",
                "developerName": "AshteMobile",
                "subtitle": "Modded Game",
                "localizedDescription": "Downloaded from AshteMobile",
                "iconURL": "https://ashtemobile.site/logo.png",
                "tintColor": "#04ecfc",
                "category": "games",
                "screenshots": [],
                "versions": [
                    {
                        "version": "1.0.0",
                        "date": "2026-09-26T14:43:39.000000Z",
                        "localizedDescription": None,
                        "downloadURL": download_url,
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
        
    print(f"Successfully processed {len(all_apps)} apps.")

if __name__ == '__main__':
    generate_ashteipa()
