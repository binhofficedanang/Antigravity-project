import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# 1. raovatdanang.vn
try:
    print("=== raovatdanang.vn links ===")
    res = requests.get("https://raovatdanang.vn/", headers=headers, timeout=5, verify=False)
    soup = BeautifulSoup(res.text, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if any(w in href.lower() or w in text.lower() for w in ["dang", "post", "login", "register", "tai-khoan"]):
            print(f"Link: {text} -> {href}")
except Exception as e:
    print("Error:", e)

# 2. chodanang.com
try:
    print("=== chodanang.com links ===")
    res = requests.get("http://chodanang.com/", headers=headers, timeout=5, verify=False)
    soup = BeautifulSoup(res.text, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if any(w in href.lower() or w in text.lower() for w in ["dang", "post", "login", "register", "tai-khoan", "nhap"]):
            print(f"Link: {text} -> {href}")
except Exception as e:
    print("Error:", e)
