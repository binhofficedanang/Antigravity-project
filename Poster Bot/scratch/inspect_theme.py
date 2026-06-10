import requests
from bs4 import BeautifulSoup

url = "https://propertydanang.com/property/toa-nha-vietinbank/"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    print("=== WEBSITE TITLE ===")
    print(soup.title.string.strip() if soup.title else "None")
    
    print("\n=== HEADINGS ===")
    for h in soup.find_all(["h1", "h2"]):
        print(f"{h.name}: {h.get_text().strip()}")
        
    print("\n=== COMMON CLASS SELECTORS ===")
    selectors = [
        ".property-address", ".address", "[class*='address']",
        ".property-area", ".area", "[class*='area']",
        ".property-price", ".price", "[class*='price']",
        ".property-description", ".entry-content", ".content",
        ".ere-property-element", ".property-meta"
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            print(f"Selector '{sel}': found | Text: '{el.get_text().strip()[:100]}...'")
        else:
            print(f"Selector '{sel}': NOT found")
            
    print("\n=== A TAGS (MAPS & LOCATION) ===")
    for a in soup.find_all("a", href=True):
        href = a['href']
        if "maps.google" in href or "google.com/maps" in href or "/location/" in href or "/area/" in href:
            print(f"A Tag: href='{href}' | Text='{a.get_text().strip()}'")

except Exception as e:
    print(f"Error inspecting site: {e}")
