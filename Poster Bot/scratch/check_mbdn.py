import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

try:
    res = requests.get("https://muabandanang.vn/", headers=headers, timeout=10)
    print("Status:", res.status_code)
    soup = BeautifulSoup(res.text, "html.parser")
    print("Title:", soup.title.string if soup.title else "No Title")
    
    # Print registration/login links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if any(w in href.lower() or w in text.lower() for w in ["dang", "post", "login", "register", "nhap", "ky"]):
            print(f"Link: {text} -> {href}")
except Exception as e:
    print("Error:", e)
