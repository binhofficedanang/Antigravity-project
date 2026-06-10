import urllib.request
import urllib.error
import socket
from bs4 import BeautifulSoup
import re

sites = [
    {"name": "123nhadatviet.com", "base": "http://123nhadatviet.com"},
    {"name": "vatgia.com", "base": "https://www.vatgia.com"},
    {"name": "nhadatviet247.net", "base": "http://nhadatviet247.net"},
    {"name": "batdongsangiatot.com.vn", "base": "https://batdongsangiatot.com.vn"},
    {"name": "dangtinbatdongsan.vn", "base": "https://dangtinbatdongsan.vn"},
    {"name": "chonhadat24h.com", "base": "https://chonhadat24h.com"}
]

socket.setdefaulttimeout(10)

print("=== KIỂM TRA LIÊN KẾT ĐĂNG NHẬP TRÊN TRANG CHỦ ===")
for s in sites:
    print(f"\nSite: {s['name']} (Base: {s['base']})")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(s['base'], headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find links with texts or hrefs containing "đăng nhập", "login", "dang-nhap"
            links = soup.find_all("a")
            found_links = []
            for link in links:
                href = link.get("href") or ""
                text = link.get_text().strip().lower()
                
                # Check match
                is_match = False
                if any(k in href.lower() for k in ["login", "dang-nhap", "dangnhap", "signin"]):
                    is_match = True
                if any(k in text for k in ["đăng nhập", "login", "đăng ký", "register"]):
                    is_match = True
                    
                if is_match:
                    found_links.append({"text": text, "href": href})
                    
            print(f"  Found {len(found_links)} candidate links:")
            for fl in found_links[:6]:
                print(f"    - Text: '{fl['text']}' -> Href: '{fl['href']}'")
    except Exception as e:
        print(f"  ⚠️ Error scraping: {e}")
