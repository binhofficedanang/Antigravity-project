import urllib.request
import urllib.error
import socket
from bs4 import BeautifulSoup

sites = [
    {"name": "123nhadatviet.com", "base": "http://123nhadatviet.com"},
    {"name": "vatgia.com", "base": "https://www.vatgia.com"},
    {"name": "nhadatviet247.net", "base": "http://nhadatviet247.net"},
    {"name": "batdongsangiatot.com.vn", "base": "https://batdongsangiatot.com.vn"},
    {"name": "dangtinbatdongsan.vn", "base": "https://dangtinbatdongsan.vn"},
    {"name": "chonhadat24h.com", "base": "https://chonhadat24h.com"}
]

paths = ["/dang-nhap", "/login", "/wp-login.php", "/tai-khoan", "/user/login", "/dangnhap"]
socket.setdefaulttimeout(8)

print("=== KIỂM TRA ĐƯỜNG DẪN ĐĂNG NHẬP ===")
for s in sites:
    print(f"\nSite: {s['name']} (Base: {s['base']})")
    found_login = False
    for path in paths:
        url = s['base'] + path
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    html = response.read()
                    soup = BeautifulSoup(html, 'html.parser')
                    forms = soup.find_all("form")
                    print(f"  🟢 Found 200 OK at {path} ({len(forms)} forms)")
                    found_login = True
                    # Check if there is password or username fields
                    for idx, f in enumerate(forms):
                        inputs = [inp.get("name") or inp.get("id") or inp.get("type") for inp in f.find_all("input")]
                        print(f"    - Form {idx}: inputs={inputs}")
                    break
        except urllib.error.HTTPError as e:
            pass
        except Exception as e:
            pass
            
    if not found_login:
        print("  🔴 No login path found in default list.")
