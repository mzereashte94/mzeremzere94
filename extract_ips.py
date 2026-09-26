import json
import requests
import re
from bs4 import BeautifulSoup
import os

HTML_FILE = "checkover.html"
OUTPUT_FILE = "ashteips.json"

def extract_copy_links():
    if not os.path.exists(HTML_FILE):
        print("فایلا checkover.html نەهاتە دیتن! لڤێرە دڤێت فایلا HTML هەبیت.")
        return

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    app_div = soup.find('div', id='app')

    if not (app_div and app_div.has_attr('data-page')):
        print("ناتوانین داتایێن پەڕی د ناڤ HTML دا بدۆزین.")
        return

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        page_data = json.loads(app_div['data-page'])
        apps_list = page_data.get('props', {}).get('paginator', {}).get('data', [])
        
        extracted_apps = []
        print(f"ئەڤ چەند یاری هاتنە دیتن: {len(apps_list)}. دەستپێکرنا دەرهێنانا لێنکان...")
        
        for idx, app in enumerate(apps_list):
            name = app.get('name', 'یاریا نەناسراو')
            uuid = app.get('uuid')
            
            download_page_url = f"https://check0ver.net/en/iapps/{uuid}/download" if uuid else ""
            copy_link_url = download_page_url 
            
            if download_page_url:
                print(f"دەرهێنانا لینکێ: {name}...")
                try:
                    response = requests.get(download_page_url, headers=headers, timeout=10)
                    
                    # گەڕیان ل دیڤ لێنکێ ڕاستەقینە یێ API کو ?ref= تێدایە (لێنکێ Click to copy)
                    match = re.search(r'(https://check0ver\.net/api/check0ver/[^"\'\s]+\.ipa\?ref=[A-Za-z0-9+/=]+)', response.text)
                    
                    if match:
                        copy_link_url = match.group(1).replace('\\/', '/')
                    else:
                        detail_soup = BeautifulSoup(response.text, 'html.parser')
                        inputs = detail_soup.find_all('input', type='text')
                        for inp in inputs:
                            if inp.get('value', '').startswith('https://check0ver.net/api/'):
                                copy_link_url = inp['value']
                                break
                except Exception as e:
                    print(f"  -> خەلەت ڕوویدا بۆ {name}: {e}")
            
            extracted_apps.append({
                "id": str(88000000 + idx),
                "name": name,
                "version": app.get('version', '1.0'),
                "size": app.get('size', 'N/A'),
                "icon": app.get('image', 'https://ashtemobile.site/logo.png'),
                "install_url": copy_link_url, 
                "download_url": copy_link_url,
                "developerName": "AshteMobile",
                "localizedDescription": f"Extracted via API: {app.get('description', name)}"
            })
            
        # پاراستنا زانیارییان د ناڤ فایلا ashteips.json دا
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as json_file:
            json.dump(extracted_apps, json_file, indent=2, ensure_ascii=False)
            
        print(f"\n سەرکەفتبوو! هەمی لێنک د فایلا {OUTPUT_FILE} دا هاتنە پاراستن.")
        
    except json.JSONDecodeError:
        print("خەلەت د شیکرنەوەا داتایێن JSON دا.")

if __name__ == '__main__':
    extract_copy_links()
