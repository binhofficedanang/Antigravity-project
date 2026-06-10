import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# 1. raovatdanang.vn
try:
    res = requests.get("https://raovatdanang.vn/", headers=headers, timeout=5, verify=False)
    html = res.text.lower()
    print("=== raovatdanang.vn ===")
    if "xenforo" in html:
        print("CMS: XenForo")
    elif "vbulletin" in html or "vbcms" in html:
        print("CMS: vBulletin")
    elif "wp-content" in html or "wordpress" in html:
        print("CMS: WordPress")
    else:
        print("CMS: Custom / Other")
    
    # search for login links
    login_links = [href for href in list(set(requests.utils.default_headers().keys()))] # dummy
    import re
    links = re.findall(r'href=["\'](.*?)(dang-nhap|login|sign-in|signin)["\']', html)
    print("Login paths found:", links)
except Exception as e:
    print("raovatdanang.vn check failed:", e)

# 2. chodanang.com
try:
    res = requests.get("http://chodanang.com/", headers=headers, timeout=5, verify=False)
    html = res.text.lower()
    print("=== chodanang.com ===")
    if "xenforo" in html:
        print("CMS: XenForo")
    elif "vbulletin" in html or "vbcms" in html:
        print("CMS: vBulletin")
    elif "wp-content" in html or "wordpress" in html:
        print("CMS: WordPress")
    else:
        print("CMS: Custom / Other")
    links = re.findall(r'href=["\'](.*?)(dang-nhap|login|sign-in|signin)["\']', html)
    print("Login paths found:", links)
except Exception as e:
    print("chodanang.com check failed:", e)
