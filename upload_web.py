import os
import re
import requests
import subprocess
from bs4 import BeautifulSoup

print("=== ASHTE MOBILE: WEB SCRAPER & UPLOADER ===")

TARGET_URL = "https://ashtemobile.tututweak.com/o.html"
RELEASE_TAG = "V1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def upload_to_github(file_path, tag):
    print(f"🚀 Uploading {file_path} to Release '{tag}'...")
    try:
        subprocess.run(["gh", "release", "upload", tag, file_path, "--clobber"], check=True)
        print("✅ Upload successful!")
    except Exception as e:
        print(f"❌ Failed to upload: {e}")

try:
    print(f"🔄 Fetching page: {TARGET_URL}")
    response = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
    
    if response.status_code != 200:
        print(f"❌ Failed to load website. Status code: {response.status_code}")
        exit(1)

    # بەکارهێنانی BeautifulSoup بۆ خوێندنەوەی HTMLـی وێبسایتەکە
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # دۆزینەوەی کارتەکان یان دوگمەکانی داونلۆد
    # (پشت بە شێوازی تگەکانی وێبسایتەکەت دەبەستین)
    downloads = []
    
    # گەڕان بەدوای هەموو لینکەکان یان دوگمەکانی داونلۆد لە پەڕەکەدا
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '.ipa' in href or 'download' in href:
            # دۆزینەوەی ناوی یارییەکە لە نزیک لینکەکە
            parent = a.find_parent('div')
            name = "App_Game"
            if parent:
                title_tag = parent.find(['h2', 'h3', 'h4', 'span', 'p'])
                if title_tag:
                    name = title_tag.get_text(strip=True)
            
            downloads.append({"name": name, "url": href})

    print(f"📦 Found {len(downloads)} apps to process.\n")

    for item in downloads:
        name = item["name"]
        url = item["url"]
        
        safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
        ipa_filename = f"{safe_name}.ipa"

        print(f"🔄 Processing: {name}")
        print(f"⬇️ Downloading from: {url}")
        
        try:
            with requests.get(url, headers=HEADERS, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(ipa_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            upload_to_github(ipa_filename, RELEASE_TAG)
            os.remove(ipa_filename)
            print(f"🗑️ Cleaned up local file {ipa_filename}.\n")

        except Exception as e:
            print(f"❌ Error downloading {name}: {e}\n")

except Exception as e:
    print(f"❌ Critical Error: {e}")

print("🎉 ALL DONE!")
