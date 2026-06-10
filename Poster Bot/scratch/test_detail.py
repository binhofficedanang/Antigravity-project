import requests
from bs4 import BeautifulSoup
import re

url = "https://officedanang.vn/property/toa-nha-thanh-cong/"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')

print("=== ALL H1 ELEMENTS ===")
for h1 in soup.find_all("h1"):
    print(f"H1 tag: '{h1}' | text: '{h1.get_text().strip()}'")

print("\n=== BREADCRUMBS OR ARCHIVE LINKS ===")
for a in soup.find_all("a", href=True):
    href = a['href']
    if "/location/" in href:
        print(f"Location Link: text='{a.get_text().strip()}' | href='{href}'")

print("\n=== GOOGLE MAPS LINKS ===")
for a in soup.find_all("a", href=True):
    href = a['href']
    if "maps.google" in href or "google.com/maps" in href:
        print(f"Maps Link: text='{a.get_text().strip()}' | href='{href}'")

print("\n=== DISTRICT MATCHES IN CONTENT ===")
# Tìm từ khóa Quận ở trong các phần tử cụ thể thay vì cả trang
content_div = soup.select_one(".property-description, .entry-content, .content, .ere-property-element")
if content_div:
    text = content_div.get_text()
    for d in ["Hải Châu", "Thanh Khê", "Cẩm Lệ", "Sơn Trà", "Liên Chiểu", "Ngũ Hành Sơn"]:
        if d.lower() in text.lower():
            print(f"Match found in content: {d}")
else:
    print("No content div found")

