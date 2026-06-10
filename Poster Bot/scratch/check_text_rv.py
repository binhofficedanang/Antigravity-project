import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

try:
    res = requests.get("https://raovatdanang.vn/", headers=headers, timeout=10)
    print("Status:", res.status_code)
    soup = BeautifulSoup(res.text, "html.parser")
    print("Page Title:", soup.title.string if soup.title else "No Title")
    print("Page body text snippet:\n", soup.get_text()[:1000])
except Exception as e:
    print("Error:", e)
