import requests
from bs4 import BeautifulSoup

url = "https://propertydanang.com/property/toa-nha-vietinbank/"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    print("=== LIST LINED ITEMS ===")
    for el in soup.select('.list-lined-item'):
        print(f"Item HTML: {el}")
        print(f"Item Text: {el.get_text().strip()}")
        print("-" * 50)
        
except Exception as e:
    print("Error:", e)
