import json
import re
import requests

def extract_ipa_links():
    url = "https://ashtemobile.tututweak.com/o.html"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
    }
    
    print(f"Fetching data from {url}...")
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # پاککردنەوەی دەقی ماڵپەڕەکە لە نیشانەی زیادە کە زۆرجار لینکەکان دەشارنەوە
            clean_text = response.text.replace('\\/', '/')
            
            # گەڕان بەدوای هەموو جۆرە لینکێکدا لەناو ماڵپەڕەکە
            all_urls = re.findall(r'(https?://[^\s"\'<>\[\]]+)', clean_text)
            
            # جیاکردنەوەی تەنها ئەو لینکانەی کە .ipa یان تێدایە
            ipa_links = [link for link in all_urls if '.ipa' in link.lower()]
            
            # سڕینەوەی لینکە دووبارەکان
            unique_links = list(set(ipa_links))
            
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
                
            print(f"Successfully extracted {len(unique_links)} IPA links and saved to '{output_filename}'.")
        else:
            print(f"Failed to fetch the page. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    extract_ipa_links()
