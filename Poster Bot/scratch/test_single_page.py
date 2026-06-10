import requests
from bs4 import BeautifulSoup
import re

url = "https://propertydanang.com/property/toa-nha-vietinbank/"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # 1. Title
    title = soup.find('h1').get_text().strip() if soup.find('h1') else ""
    print("Title:", title)
    
    # 2. Address
    address_el = soup.find('address', class_='item-address')
    address = address_el.get_text().strip() if address_el else ""
    print("Address:", address)
    
    # 3. Price
    price_el = soup.select_one('.item-price-wrap .price, .property-price-wrap .price, span.price')
    price = price_el.get_text().strip() if price_el else ""
    print("Price:", price)
    
    # 4. Description content
    desc_el = soup.select_one('.property-description-content, .description-content, .block-content-wrap')
    desc_text = desc_el.get_text().strip() if desc_el else ""
    print("Desc Text length:", len(desc_text))
    
    # 5. Let's find any text matching areas (e.g. 100m2, 100 - 200, diện tích, v.v...)
    print("\n=== SEARCHING FOR AREA / DIỆN TÍCH TEXTS ===")
    all_text = soup.get_text()
    for line in all_text.split('\n'):
        line = line.strip()
        if any(keyword in line.lower() for keyword in ["diện tích", "m2", "m²", "diện tích trống", "khai thác"]):
            if len(line) > 5 and len(line) < 150:
                print("Line:", line)
                
except Exception as e:
    print("Error:", e)
