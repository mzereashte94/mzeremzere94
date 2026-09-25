import json
import requests
from datetime import datetime

print("=== ASHTE MOBILE: FULL IPA EXTRACTOR WITH COOKIE ===")

json_file = "ashtemobile94.json"
base_url = "https://check0ver.net/en/iapps"
api_url = "https://check0ver.net/api/iapps/{}/download"

# کۆکییەکەی تۆ کە لە وێنەکەدا نیشانت داوە
MY_COOKIE = "XSRF-TOKEN=eyJpdiI6Im9XeXVOWXhvdzZFaVVtUTJkbYJqWXZFOTPSIsInZhbHVlIjoiT0hwRzB4TlhEWmJjVkV5UzhzU1ZVUi00b1dJOUxSRkV2VUM5R2FVWlBORlZ4T0ZGbklKU1BGVjNXRFZKUzBkcFZWWkRkVTFTMjEwVFBUVVY1U1dWdkNGZTVYaTgzV0ltTXkxa1ZoSFhrZGFWM1B5M2s1YVRSSU0welpZV3VUM0N2VEdXWmNYWkRRdWQxdGRYbzBUMUpiMWlMQ0p0WVdNaU9pbzFOekU1TldRNFlqSTBPRGN6T1RSa1l6UXhPVEEzTXpZM1pUY3hPVEEzT0RWbVlUSmlNRFF4TldRMVkyUmxNalExTVROak5qaGhNRGhsWmpWaU1EVTBNamszWmpsaU1qWXpaVEl4T1dKaVkyVTNZelF3TWpaaFlqUm1ZV1JoT1RWak4yVXpaakU1TkRSaE1UQXhaVGN4T1RKak1UUm1aVGd6TTJVd05qYzBOREppWmpBNVkyRTVNamhtTXpFek1XUmhaVEF3TURnNE1UZ3pNams1TkROa09UZGhaVGxoTWpaalpUYzNZbVF5WWpJNE5UbGtOVGRtTVRCa04yUm1aamhrTkRoaU0yVTFPVEExTURNeE1XUmpOVEF5TnpRMFpUSXlOR0UyTVdNNFpESTBOVGM0TXpFeE1EUTFNakpqTldVNU9EVmlPV0psT1RFM00yUTNOakV4Wm1Vd01UQmhZakZqT0RKbU16QXlOVEl5TkRKallUTTRPREkyTURBek0yRTVOekJoWTJSbU0yUTVZell6WWpobU5qSTJNelEzWXpaa01HVmpZamhpWmpoa1lXUmlOemd3WVRJM01ESTVZMlkxTXpBNFkyVmtZMlEzWXpFelpXWTBOMkpsTVRrME9UTTJNamxqTW1NNVptUTRNVFkzTWpFNE1ETmhObUU1TlRGaE9HWmlPVEJsTmpjMk4yWTJPVEl3TmpZd1pETmlNemRqWWpsaU0yWmxOelE1WXpsbVpUQTRZMlk0WXpVNVpXWTRaRFpoWXpNMU0yWTBZbUkyTlRWalltRTJOelE0WlRKbFlUTTBObUUyT0RabU5UTXdOVFF4TnpneE5qWXpNVGN6TTJZMFptWTFOMk0xTmpaaE5EZG1OV1ZqTjJWak9EZGhaalUxTTJaalltWTFNRFF3T0RjMk1ERXdPRGc0TmpJMU5UVmhaamcwTm1RNFltWTFNRFU0T0RSaFpEQmhNMkprWldOa05EbG1OV1ExWlROa01XVXdPVFZtTkRsak5ETTVNemhqTmpFeFkyVTJZbVEzWVdRNFkySmpPRGt6TjJKbU9URXdNMlZrT0RZd1ltRTBZMkUyWkdNNFlXTTVOVGhtWmpsak9HWmxObVE0WlRSa1pUZG1ZMkpqTmpRMk16Y3dObVk1TmpabVpUSmhOR1ZtWVRSaFltVTVNR0UwTXpFek9HSmxZV1JtWmpGak5EUXpaRFpqT0RCa09XUmhaVEkyWlRreFlUbGtZbVF4TkdGaE9UZ3lNMlEzWXpOaU1EUXdPV015TkRSak4yVXlOemsyTWpnM01XRXdZMkl3WVROa1lUY3dORFZtTmpRNE5UbGxZVEl6TWpReU0ySThPVGRoWmpsak1UZ3pNREUwTURZMllUZ3dNVGc1T1RGbVpXVXhaVGd4WmpsbU1UVmpPVEJsWWprNE4yWTFOVE00TVdReFptWTFOMlJoWWpkak4yRmhZelUxWmpJeVlXUTNPVEJtTWpoak5XUTVOelpsWWpsaFptTXlOemMwWldKaU5XTTFOVGt6T1RZd01UTTJNMlk0WVRCbU1XRTBZVFprTURFME0yUTVNREV4WmpjNU9ESXdOelZpTTJZMFlqRTVZakExTmpJeFptRXpaalEzTXpOaE5tUTVNekJoTmpNM1lXUmhZemRoT1dRM05UUTBOREV5TkRabE0yVmhaRGhtTkRJMVl6azFNemhpWkdZMFlqZG1ORFF4TnpWa1pHSTNaV0l3WWpBNFpqZ3pNbVU1TWpkbU9HVmxOVGd6TmpReVlUUmhNakV4TXpaallUSTBPVEk1TTJVME1HVm1abUl4TVdabVpHVmxabVZqT0RsbE1HRmxZV1psWldVM09UUmpaakZtTkRJMFlqUTNOakk1WWpaaFpUQTVZekkxWmpreU1HRmhaREV6TmpsbFpHWTJZbUZqTjJaalpqSTBOV0ZpT0RKak9EVmpabVk0TkRCak0ySmpNMkpoWTJRd05EazNNekExTURobFpqQmhaRE01TWpNMVlqZzNPVEZqTVdJeFptSTBNMlppTm1GaE5XTXdNV0V4TkdJM1pHWmpPR0pqT1dJMVpUQXdORFF6WTJGbFkyWTRNVFF4WWpVNVlXTmhNVFEyWkRNMVlXVXdPREE0TTJFME5XUT1cIiB9; checkover_session=eyJpdiI6ImNoc1h4UVNFYTZIMTJ4ZEM3R3QyRkE9PSIsInZhbHVlIjoidFieVg3d3RQT2VPUXFHRTl0V1Q1U1JWRk4xSm9Za05hVldvNExPUUJNRk0wWjB4TVp6UmthMUZZZFVaS2JFOTBVbnA2YTBoelJTOTViVEpHTVdoamVVa3hhRVJpZGtWUWFIZGphMDQzSzNOQ1oxRjJOVTlQWm5oeFdVUzNSV3BsVVpaaVFrSlJWR2RJTkZSVVNURnJhVk5rZVRCVVZHcFNTRTBpTENKdFlXTWlPaUpuWmc0TXpGaU9XTXhaR0kwWTJRM05HWTRNRGMwT0dSSVpXTTBPVEZoWXpkbU16ZzFZenEzTW1ZMk16QTNZVGRoTlRJMFRka1lUZE56YzBRaWwwSUQ9PSJ9"

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.6.1 Mobile/15E148 Safari/604.1",
    "Accept": "application/json, text/plain, */*",
    "X-Inertia": "true",
    "X-Inertia-Version": "mimusoft-ipa-check0ver-customer-1.0.0",
    "Cookie": MY_COOKIE,
    "Referer": "https://check0ver.net/en/iapps"
}

apps_list = []

try:
    print("Fetching data from website...")
    # هێنانی داتاکان بە بەکارهێنانی کۆکی[span_0](start_span)[span_0](end_span)
    response = requests.get(base_url, headers=headers, timeout=15)
    
    if response.status_code == 200:
        page_data = response.json()
        games = page_data.get("props", {}).get("paginator", {}).get("data", [])
        print(f"Found {len(games)} games. Extracting real .ipa links...")
        
        for game in games:
            uuid = game.get("uuid")
            name = game.get("name")
            version = game.get("version", "1.0")
            bundle_id = game.get("bundle", f"com.ashtemobile.{uuid}")
            icon = game.get("image", "https://ashtemobile.site/logo.png")
            desc = game.get("description", "Auto extracted app")
            
            # لینکی یەدەگ
            dl_link = f"https://check0ver.net/en/iapps/{uuid}"
            
            # هەوڵدان بۆ هێنانی لینکی ڕاستەقینەی کە refـی تێدایە[span_1](start_span)[span_1](end_span)
            try:
                dl_response = requests.get(api_url.format(uuid), headers=headers, allow_redirects=False, timeout=10)
                
                if dl_response.status_code == 200:
                    try:
                        dl_json = dl_response.json()
                        dl_link = dl_json.get("url", dl_json.get("download_url", dl_link))
                    except:
                        pass
                elif dl_response.status_code in [301, 302, 303, 307, 308]:
                    dl_link = dl_response.headers.get("Location", dl_link)
                    
            except Exception as e:
                print(f"Error getting link for {name}: {e}")
            
            print(f"Extracted: {name} -> {dl_link[:50]}...")
            current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
            
            apps_list.append({
                "name": name,
                "bundleIdentifier": bundle_id,
                "developerName": "CheckOver",
                "version": version,
                "versionDate": current_time,
                "versionDescription": "Direct CDN Link",
                "downloadURL": dl_link,
                "localizedDescription": desc,
                "iconURL": icon,
                "tintColor": "#04ecfc",
                "size": 314572800,
                "versions": [
                    {
                        "version": version,
                        "date": current_time,
                        "localizedDescription": "Latest release",
                        "downloadURL": dl_link,
                        "size": 314572800,
                        "minOSVersion": "14.0"
                    }
                ]
            })
    else:
        print(f"Failed to fetch page. Status: {response.status_code}")
        
except Exception as e:
    print(f"Fatal error: {e}")

source_structure = {
    "name": "Ashtemobile",
    "identifier": "com.ashtemobile.source", 
    "subtitle": "Ksign & Feather Source",
    "description": "Auto Generated Full Catalog with Direct Links.",
    "iconURL": "https://ashtemobile.site/logo.png",
    "website": "https://ashtemobile.site/",
    "tintColor": "#ff007f",
    "apps": apps_list,
    "news": []
}

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(source_structure, f, ensure_ascii=False, indent=4)

print(f"\nSUCCESS! Saved {len(apps_list)} apps.")
