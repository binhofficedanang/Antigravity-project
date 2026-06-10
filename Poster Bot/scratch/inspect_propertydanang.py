import requests
from bs4 import BeautifulSoup
import re

url = "https://propertydanang.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # In tất cả các link
    links = []
    for a in soup.find_all("a", href=True):
        href = a['href']
        links.append(href)
        
    print(f"Total links found: {len(links)}")
    
    # Lọc các link đặc trưng (như property, category, location, v.v...)
    property_links = [l for l in links if "/property/" in l or "/property_type/" in l or "/location/" in l or "/estate/" in l or "/tin-dang/" in l]
    print(f"Interesting links ({len(property_links)}):")
    for l in set(property_links[:30]):
        print("  -", l)
        
    # In một số link ngẫu nhiên/khác của website để xem cấu trúc
    print("Other distinct links sample:")
    distinct_links = sorted(list(set(links)))
    for l in distinct_links[:40]:
        print("  -", l)
        
except Exception as e:
    print(f"Error inspecting site: {e}")
