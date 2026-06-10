import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for url in ["https://propertydanang.com", "https://officedanang.vn"]:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No Title"
        print(f"URL: {url} | Status: {r.status_code} | Title: {title}")
    except Exception as e:
        print(f"URL: {url} | Error: {e}")
