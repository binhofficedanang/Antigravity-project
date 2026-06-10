import requests
from bs4 import BeautifulSoup

url = "https://officedanang.vn/property/toa-nha-thanh-cong/"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')

print("=== ALL H1 ELEMENTS ===")
for h1 in soup.find_all("h1"):
    print(f"H1 tag: '{h1}' | text: '{h1.get_text().strip()}'")

print("\n=== SPECIFIC SELECTORS ===")
print("h1.entry-title:", soup.select_one("h1.entry-title"))
print("h1.ere-property-title:", soup.select_one("h1.ere-property-title"))
print(".property-title:", soup.select_one(".property-title"))
print("title tag:", soup.title.string if soup.title else "None")
