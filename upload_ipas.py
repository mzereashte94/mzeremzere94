import json
import os
import requests
import subprocess

print("=== ASHTE MOBILE: AUTO IPA DOWNLOADER & UPLOADER ===")

API_TOKEN = "33833|hNBTRwESKR8UJGSdTO6O1PzF35LT0WJNyHKsA5925266286a"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.55 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Accept": "application/json"
}

# ناوی ئەو ڕیلیزەی کە دەتەوێت فایلەکانی تێدا دابنێیت
RELEASE_TAG = "V1" 

def upload_to_github(file_path, tag):
    print(f"🚀 Uploading {file_path} to Release '{tag}'...")
    try:
        # بەکارهێنانی فەرمانی gh بۆ بەرزکردنەوەی فایلەکە
        subprocess.run(["gh", "release", "upload", tag, file_path, "--clobber"], check=True)
        print("✅ Upload successful!")
    except Exception as e:
        print(f"❌ Failed to upload: {e}")

try:
    with open("ashtemobile94.json", "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    print("❌ Could not read JSON file. Make sure it exists.")
    exit(1)

apps = data.get("apps", [])
print(f"📦 Found {len(apps)} apps in JSON. Starting process...\n")

for app in apps:
    name = app.get("name")
    download_trigger_url = app.get("downloadURL")
    
    # خاوێنکردنەوەی ناوی یارییەکە بۆ ئەوەی کێشە لە فایلی .ipa دروست نەکات
    safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
    ipa_filename = f"{safe_name}.ipa"

    print(f"🔄 Processing: {name}")
    try:
        # 1. وەرگرتنی لینکی ڕاستەقینەی داونلۆدەکە لە Check0ver
        res = requests.get(download_trigger_url, headers=HEADERS, allow_redirects=False, timeout=15)
        real_link = None
        
        if res.status_code in [301, 302, 303, 307, 308]:
            real_link = res.headers.get("Location")
        elif res.status_code == 200:
            try:
                real_link = res.json().get("url")
            except:
                pass
                
        if not real_link or "ref=" not in real_link:
            print(f"⚠️ Could not find CDN link for {name}. Skipping...\n")
            continue

        print(f"⬇️ Downloading {ipa_filename} (This might take a while depending on size)...")
        
        # 2. داونلۆدکردنی یارییەکە بە شێوازی پارچە پارچە بۆ ئەوەی ڕام پڕ نەبێت
        with requests.get(real_link, headers=HEADERS, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(ipa_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        # 3. بەرزکردنەوەی بۆ بەشی Releases لە گیت هاب
        upload_to_github(ipa_filename, RELEASE_TAG)

        # 4. سڕینەوەی یارییەکە لەناو سێرڤەر بۆ ئەوەی جێگەی یارییەکەی تر ببێتەوە
        os.remove(ipa_filename)
        print(f"🗑️ Deleted local file {ipa_filename} to save space.\n")

    except Exception as e:
        print(f"❌ Error processing {name}: {e}\n")

print("🎉 ALL DONE!")
