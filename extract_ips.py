import json
import re
import requests

def extract_ipa_links():
    url = "https://ashtemobile.tututweak.com/o.html"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
            "AppleWebKit/605.1.55 (KHTML, like Gecko) Version/16.0 Mobile/15E148 "
            "Safari/604.1"
        )
    }
    
    print(f"Fetching data from {url}...")
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # گەڕان بەدوای هەموو ئەو لینکانەی کە درێژکراوەی .ipa یان تێدایە
            pattern = r'https?://[^\s"\'<>]+?\.ipa[^\s"\'<>]*'
            
            # دەرهێنانی هەموو لینکەکان لەناو کۆدی HTMLـی ماڵپەڕەکە
            raw_links = re.findall(pattern, response.text)
            
            # سڕینەوەی لینکە دووبارەکان بۆ ئەوەی هەر یارییەک تەنها یەک جار زیاد بکرێت
            unique_links = list(set(raw_links))
            
            apps_list = []
            for index, link in enumerate(unique_links):
                # ڕێکخستنی زانیارییەکان بۆ ناو فایلی جەیسن
                apps_list.append({
                    "id": index + 1,
                    "name": f"App_{index + 1}", 
                    "download_url": link
                })
            
            # دروستکردنی پێکهاتەی کۆتایی فایلەکە
            output_data = {
                "source_website": url,
                "total_links_found": len(unique_links),
                "apps": apps_list
            }
            
            # پاشەکەوتکردنی داتاکان لەناو فایلی ashteips.json
            output_filename = "ashteips.json"
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=4)
                
            print(f"Successfully extracted {len(unique_links)} IPA links and saved to '{output_filename}'.")
        else:
            print(f"Failed to fetch the page. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    extract_ipa_links()
