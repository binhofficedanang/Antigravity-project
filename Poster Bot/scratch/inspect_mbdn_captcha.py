import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

try:
    res = requests.get("https://muabandanang.vn/dang-ky", headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    captcha_input = soup.find("input", id="captcha")
    if captcha_input:
        # Check parents or siblings of this element
        parent = captcha_input.parent
        print("Captcha parent HTML:\n", parent.prettify())
except Exception as e:
    print("Error:", e)
