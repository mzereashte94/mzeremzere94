import json
import requests
import os
import re

JSON_FILE = 'ashteips.json'

def download_ipas():
    if not os.path.exists(JSON_FILE):
        print('JSON File not found!')
        return

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        apps = json.load(f)

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
    }

    for app in apps:
        name = app.get('name', 'App').replace(' ', '_').replace(':', '').replace('/', '_')
        url = app.get('download_url') or app.get('install_url')
        
        if not url or not url.startswith('http'):
            continue

        print(f'Checking link for: {name}...')
        real_ipa_url = None

        try:
            if '.ipa' in url and 'check0ver' not in url:
                real_ipa_url = url
            else:
                res = requests.get(url, headers=headers, timeout=15)
                
                ipa_matches = re.findall(r'https?://[^\s"\']+\.ipa[^\s"\']*', res.text)
                plist_matches = re.findall(r'https?://[^\s"\']+\.plist[^\s"\']*', res.text)

                if ipa_matches:
                    real_ipa_url = ipa_matches[0]
                elif plist_matches:
                    plist_res = requests.get(plist_matches[0], headers=headers, timeout=15)
                    real_ipa_matches = re.findall(r'https?://[^\s"\']+\.ipa[^\s"\']*', plist_res.text)
                    if real_ipa_matches:
                        real_ipa_url = real_ipa_matches[0]

            if real_ipa_url:
                print(f'Downloading real IPA for {name} from {real_ipa_url}...')
                ipa_res = requests.get(real_ipa_url, headers=headers, stream=True, timeout=180)
                
                if ipa_res.status_code == 200:
                    ipa_path = f'{name}.ipa'
                    with open(ipa_path, 'wb') as ipa_f:
                        for chunk in ipa_res.iter_content(chunk_size=1024*1024):
                            if chunk:
                                ipa_f.write(chunk)
                    
                    size_mb = os.path.getsize(ipa_path) / (1024 * 1024)
                    if size_mb > 1.0:
                        print(f'Successfully downloaded {ipa_path} ({size_mb:.2f} MB)')
                    else:
                        print(f'File too small ({size_mb:.2f} MB), removing...')
                        os.remove(ipa_path)
            else:
                print(f'No direct .ipa found for {name}')

        except Exception as e:
            print(f'Error processing {name}: {e}')

if __name__ == '__main__':
    download_ipas()
