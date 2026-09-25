import hashlib
import json
import re
import requests
import concurrent.futures

print("=== ASHTE MOBILE: ULTRA FAST EXTRACTOR (API TOKEN) ===")

# تووکنەکەی خۆت بۆ ئەوەی سایتەکە ڕێگەت پێ بدات
API_TOKEN = "33833|hNBTRwESKR8UJGSdTO6O1PzF35LT0WJNyHKsA5925266286a"

base_url = "https://check0ver.net/en/iapps?filter%5BinCategories%5D%5B0%5D=9c60f563-1983-42f0-8882-a26207bd4aaf&page="

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.55 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Accept": "application/json, text/html, */*"
}

print("1. Fetching all apps from the website...")
raw_apps = []
session = requests.Session()
session.headers.update(headers)

# هێنانی داتای سەرەکی لە پەڕەکانەوە
for page in range(1, 161):
    url = f"{base_url}{page}"
    try:
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            match = re.search(r'data-page="([^"]+)"', response.text)
            if match:
                html_escape_decoded = (
                    match.group(1)
                    .replace("&quot;", '"')
                    .replace("&amp;", "&")
                    .replace("&#039;", "'")
                )
                page_data = json.loads(html_escape_decoded)
                paginator = page_data.get("props", {}).get("paginator", {}).get("data", [])
                
                if not paginator:
                    break
                
                raw_apps.extend(paginator)
        else:
            break
    except Exception as e:
        pass

print(f"Found {len(raw_apps)} apps. Now extracting the EXACT .ipa links really fast...")

def get_real_ipa(app):
    uuid = app.get("uuid")
    name = app.get("name")
    version = app.get("version", "1.0")
    size_str = app.get("size", "0 MB")
    image_url = app.get("image", "https://ashtemobile.site/logo.png")
    updated_at = app.get("updatedAt", "2026-09-15T00:00:00+00:00")
    bundle = app.get("bundle", f"com.ashtemobile.{uuid}")
    
    download_trigger_url = f"https://check0ver.net/api/iapps/{uuid}/download"
    final_ipa_url = None
    
    try:
        # گرتنی ڕیدایریکتەکە
        res = session.get(download_trigger_url, allow_redirects=False, timeout=10)
        if res.status_code in [301, 302, 303, 307, 308]:
            location = res.headers.get("Location", "")
            if "ref=" in location or ".ipa" in location:
                final_ipa_url = location
        elif res.status_code == 200:
            data = res.json()
            url = data.get("url", "")
            if "ref=" in url or ".ipa" in url:
                final_ipa_url = url
    except:
        pass

    if not final_ipa_url:
        return None # ئەگەر لینکی نەدۆزیەوە، یارییەکە تێپەڕێنە

    numeric_id = int(hashlib.md5(uuid.encode()).hexdigest()[:8], 16) % (10**9)

    size_bytes = 314572800 # دیفۆڵت
    try:
        if "GB" in size_str:
            size_bytes = int(float(size_str.replace("GB", "").strip()) * 1024 * 1024 * 1024)
        elif "MB" in size_str:
            size_bytes = int(float(size_str.replace("MB", "").strip()) * 1024 * 1024)
    except:
        pass

    print(f"✅ Found Link: {name}")

    return {
        "name": name,
        "bundleIdentifier": bundle,
        "developerName": "AshteMobile / Check0ver",
        "version": version,
        "versionDate": updated_at,
        "versionDescription": "Direct CDN Link",
        "downloadURL": final_ipa_url,
        "localizedDescription": "Downloaded from AshteMobile Source.",
        "iconURL": image_url if image_url else "https://ashtemobile.site/logo.png",
        "tintColor": "#04ecfc",
        "size": size_bytes,
        "versions": [
            {
                "version": version,
                "date": updated_at,
                "localizedDescription": "Direct Release",
                "downloadURL": final_ipa_url,
                "size": size_bytes,
                "minOSVersion": "14.0",
            }
        ]
    }

apps_list = []

# 100 کرێکار بۆ خێرایی
with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    results = executor.map(get_real_ipa, raw_apps)
    for res in results:
        if res:
            apps_list.append(res)

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

output_filename = "ashtemobile94.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(source_structure, f, ensure_ascii=False, indent=4)

print(f"\nDone! Extracted EXACT .ipa URLs for {len(apps_list)} apps.")
