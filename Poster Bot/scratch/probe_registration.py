import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# 1. raovatdanang.vn
url_wp_reg = "https://raovatdanang.vn/wp-login.php?action=register"
try:
    res = requests.get(url_wp_reg, headers=headers, timeout=10, verify=False)
    print(f"raovatdanang.vn registration check: Status {res.status_code}")
    if "registerform" in res.text:
        print("Found registerform in wp-login.php?action=register")
    else:
        print("Registration via wp-login.php may be disabled or customized.")
except Exception as e:
    print("raovatdanang.vn reg error:", e)

# 2. chodanang.com
# Let's search for register pages or forms
try:
    res = requests.get("http://chodanang.com/", headers=headers, timeout=10, verify=False)
    soup = BeautifulSoup(res.text, "html.parser")
    print("=== chodanang.com register check ===")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if "đăng ký" in text.lower() or "dang-ky" in href.lower() or "register" in href.lower() or "register" in text.lower():
            print(f"Possible registration link: {text} -> {href}")
except Exception as e:
    print("chodanang.com reg check error:", e)
