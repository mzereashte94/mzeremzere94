import json
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def extract_ipa_links():
    url = "https://ashtemobile.tututweak.com/o.html"
    
    # ڕێکخستنی کرۆم بۆ ئەوەی بەبێ کردنەوەی پەنجەرە لەسەر سێرڤەر کار بکات
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    print("Starting Chrome to fetch dynamically loaded content...")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(url)
        
        # چاوەڕێکردن بۆ ماوەی ١٠ چرکە تاوەکو یارییەکان بەتەواوی لۆد دەبن
        print("Waiting for games to load...")
        time.sleep(10)
        
        page_source = driver.page_source
        clean_text = page_source.replace('\\/', '/')
        
        # گەڕان بەدوای لینکەکانی .ipa یان لینکەکانی check0ver
        pattern1 = r'(https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(?:/[^"\'\s<>\\]+)?\.ipa[^"\'\s<>\\]*)'
        pattern2 = r'(https?://check0ver\.net/api/check0ver/[^"\'\s<>\\]+)'
        
        all_links = re.findall(pattern1, clean_text) + re.findall(pattern2, clean_text)
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
        
        with open("ashteips.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
            
        print(f"Success! Found {len(unique_links)} links.")
        driver.quit()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_ipa_links()
