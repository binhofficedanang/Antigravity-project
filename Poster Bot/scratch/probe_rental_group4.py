import requests
import urllib3
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

domains = [
    "phongtro123.com", "thuephongtro.com", "chothuematbang.com.vn", "chothuenha.me",
    "chothuevanphong.vn.vn", "phongtro.me", "batdongsan.org", "chothuenha.com.vn",
    "nhachothue.vn", "thuevanphong.vn", "vanphongchothue.vn", "thuebds.com", "matbangdep.com"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

print("Checking activity of 13 rental-focused real estate sites...")
for d in domains:
    status_str = "FAILED (Down)"
    details = ""
    for proto in ["https", "http"]:
        url = f"{proto}://{d}"
        try:
            res = requests.get(url, headers=headers, timeout=5, verify=False, allow_redirects=True)
            if res.status_code == 200:
                html_lower = res.text.lower()
                final_url = res.url.lower()
                
                # Check for parked domain page
                if "hugedomains.com" in final_url or "hugedomains" in html_lower:
                    status_str = "PARKED (HugeDomains)"
                elif "namebright.com" in final_url or "namebright" in html_lower or "coming soon" in html_lower:
                    status_str = "PARKED (NameBright/Coming Soon)"
                else:
                    # Check if registration/login/post features are present
                    features = []
                    if "đăng nhập" in html_lower or "login" in html_lower or "dang-nhap" in html_lower:
                        features.append("Login")
                    if "đăng ký" in html_lower or "register" in html_lower or "dang-ky" in html_lower:
                        features.append("Register")
                    if "đăng tin" in html_lower or "post" in html_lower or "dang-tin" in html_lower:
                        features.append("Post-ad")
                        
                    feature_str = "+".join(features) if features else "No user actions found"
                    status_str = f"ACTIVE ({feature_str})"
                
                details = f"URL: {res.url}, Length: {len(res.text)}"
            else:
                status_str = f"ACTIVE (Status {res.status_code})"
                details = f"URL: {res.url}"
            break
        except Exception as e:
            details = str(e)[:60]
            
    print(f"- {d:23} -> {status_str} | {details}")
