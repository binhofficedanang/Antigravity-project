import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

domains = [
    "muabandanang.vn", "chodanang.com", "raovatdanang.vn", "muabandanang.com",
    "raovatquangnam.com", "raovathue.com", "danangplus.com", "raovatquangngai.com",
    "chomaydailoc.com", "raovatmiendung.com", "tinraovatdanang.com", "danangrao.com"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

print("Checking activity of 12 local classified sites...")
for d in domains:
    status_str = "FAILED (Down)"
    details = ""
    for proto in ["https", "http"]:
        url = f"{proto}://{d}"
        try:
            res = requests.get(url, headers=headers, timeout=5, verify=False, allow_redirects=True)
            if res.status_code == 200:
                # Check for parked domain page
                html_lower = res.text.lower()
                final_url = res.url.lower()
                
                if "hugedomains.com" in final_url or "hugedomains" in html_lower:
                    status_str = "PARKED (HugeDomains)"
                elif "namebright.com" in final_url or "namebright" in html_lower or "coming soon" in html_lower:
                    status_str = "PARKED (NameBright/Coming Soon)"
                elif "raovatdanang.vn" in d and "wp-login.php" in html_lower:
                    status_str = "ACTIVE (Blog tin tức - Khóa đăng ký)"
                else:
                    status_str = f"ACTIVE (Status {res.status_code})"
                details = f"URL: {res.url}, Length: {len(res.text)}"
            else:
                status_str = f"ACTIVE (Status {res.status_code})"
                details = f"URL: {res.url}"
            break
        except Exception as e:
            details = str(e)[:60]
            
    print(f"- {d:23} -> {status_str} | {details}")
