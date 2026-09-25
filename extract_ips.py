import json
import re
import requests
import urllib.parse

def extract_ipa_links():
    url = "https://ashtemobile.tututweak.com/o.html"
    # إضافة ترويسات (Headers) تحاكي متصفح حقيقي لتجنب الحظر
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    print(f"Fetching data from {url}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # فك تشفير النصوص في حال كانت الروابط مشفرة (مثل %2F)
            decoded_text = urllib.parse.unquote(response.text)
            
            # إصلاح العلامات المائلة المعكوسة
            clean_text = decoded_text.replace('\\/', '/')
            
            # نمط بحث قوي لاستخراج روابط ipa التي تحتوي على متغيرات طويلة
            pattern1 = r'(https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(?:/[^"\'\s<>\\]+)?\.ipa[^"\'\s<>\\]*)'
            # نمط بحث احتياطي لاستخراج روابط check0ver مباشرة
            pattern2 = r'(https?://check0ver\.net/api/check0ver/[^"\'\s<>\\]+)'
            
            raw_links1 = re.findall(pattern1, clean_text)
            raw_links2 = re.findall(pattern2, clean_text)
            
            # دمج النتائج وحذف الروابط المكررة
            all_links = raw_links1 + raw_links2
            unique_links = list(set(all_links))
            
            apps_list = []
            for index, link in enumerate(unique_links):
                apps_list.append({
                    "id": index + 1,
                    "name": f"App_{index + 1}", 
                    "download_url": link
                })
            
            output_data = {
                "source_website": url,
                "total_links_found": len(unique_links),
                "apps": apps_list
            }
            
            output_filename = "ashteips.json"
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=4)
                
            print(f"Successfully extracted {len(unique_links)} links.")
            if len(unique_links) == 0:
                print("لم يتم العثور على روابط. قد يكون الموقع محمياً بواسطة Cloudflare أو يحتاج جافاسكريبت.")
        else:
            print(f"Failed to fetch. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    extract_ipa_links()
