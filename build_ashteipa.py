import json

# لێرەدا دەتوانیت لیستەی بەرنامە و یارییەکانت دابنێیت
apps_list = [
    {
        "id": 1,
        "name": "نموونەی بەرنامە",
        "version": "1.0.0",
        "size": "50 MB",
        "icon": "img/icon.png",
        "badge": "New",
        "type": "games",
        "description": "ئەمە وەسفی بەرنامەکەیە",
        "screenshots": [],
        "install_url": "https://check0ver.net/api/check0ver/E669C4F905734AED2E9E/168198/a06c8525303e15008b3086498c666837.ipa?ref=YTltQ1lqL0NwbGlBc2JDcFNKY2FrQVdZR0htTmtoUG1YdEo2ZUxFcTAyY2duUHd5WVFSa2w0S2JDWjZDejhOYXV6R1psS0kwOE9WdlgrdHJYU0VIZk5naFFLcGVXdHhsWmM2aTFKelZmblFyQXZEQ0l6a1pxVFFzWkpTa0FSemYxNDVLVndob0VCU3luVk4zUDNDL0c1c1RyRXVVQlYzcmJxUzF3dmUwdnZYV2JGc0RBZkNYMkE0WXZyVW5vQzVo",
        "download_url": "https://check0ver.net/api/check0ver/E669C4F905734AED2E9E/168198/a06c8525303e15008b3086498c666837.ipa?ref=YTltQ1lqL0NwbGlBc2JDcFNKY2FrQVdZR0htTmtoUG1YdEo2ZUxFcTAyY2duUHd5WVFSa2w0S2JDWjZDejhOYXV6R1psS0kwOE9WdlgrdHJYU0VIZk5naFFLcGVXdHhsWmM2aTFKelZmblFyQXZEQ0l6a1pxVFFzWkpTa0FSemYxNDVLVndob0VCU3luVk4zUDNDL0c1c1RyRXVVQlYzcmJxUzF3dmUwdnZYV2JGc0RBZkNYMkE0WXZyVW5vQzVo",
        "bundleIdentifier": "com.ashtemobile.app",
        "marketplaceID": "",
        "developerName": "AshteMobile",
        "subtitle": "Awesome App",
        "localizedDescription": "Downloaded from AshteMobile Source.",
        "iconURL": "https://ashtemobile.site/logo.png",
        "tintColor": "#04ecfc",
        "category": "games",
        "versions": [
            {
                "version": "1.0.0",
                "date": "2026-09-15T00:00:00+00:00",
                "localizedDescription": None,
                "downloadURL": "https://check0ver.net/api/check0ver/E669C4F905734AED2E9E/168198/a06c8525303e15008b3086498c666837.ipa?ref=YTltQ1lqL0NwbGlBc2JDcFNKY2FrQVdZR0htTmtoUG1YdEo2ZUxFcTAyY2duUHd5WVFSa2w0S2JDWjZDejhOYXV6R1psS0kwOE9WdlgrdHJYU0VIZk5naFFLcGVXdHhsWmM2aTFKelZmblFyQXZEQ0l6a1pxVFFzWkpTa0FSemYxNDVLVndob0VCU3luVk4zUDNDL0c1c1RyRXVVQlYzcmJxUzF3dmUwdnZYV2JGc0RBZkNYMkE0WXZyVW5vQzVo",
                "size": 52428800,
                "buildVersion": None,
                "minOSVersion": "14.0"
            }
        ],
        "appPermissions": {
            "entitlements": [],
            "privacy": {}
        },
        "patreon": []
    }
]

# پێکهاتەی سەرەکی فایلی JSON بۆ ماڵپەڕەکەت
source_structure = {
    "name": "Ashtemobile",
    "subtitle": "A source for all of my apps & games",
    "description": "Welcome to my source! Here you'll find all of my apps.",
    "iconURL": "https://ashtemobile.site/logo.png",
    "website": "https://ashtemobile.site/",
    "patreonURL": "https://ashtemobile.site/ashteipa.json",
    "tintColor": "#ff007f",
    "featuredApps": [],
    "headerURL": "https://ashtemobile.site/logo.png",
    "apps": apps_list,
    "news": [
        {
            "title": "Instagram",
            "identifier": "news_instagram",
            "caption": "Ashtemobile",
            "date": "2026-09-15T00:00:00+00:00",
            "tintColor": "#ff007f",
            "imageURL": "https://ashtemobile.site/logo.png",
            "notify": True,
            "url": "https://www.instagram.com/ashtemobile",
            "appID": None
        }
    ]
}

# پاشەکەوتکردنی داتاکە لە فایلی ashteipa.json
output_filename = "ashteipa.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(source_structure, f, ensure_ascii=False, indent=4)

print(f"File '{output_filename}' successfully created with clean links!")
