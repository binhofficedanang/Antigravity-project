import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import socket

sites = [
    "http://123nhadatviet.com",
    "https://www.vatgia.com",
    "http://nhadatviet247.net",
    "https://batdongsangiatot.com.vn",
    "https://dangtinbatdongsan.vn",
    "https://chonhadat24h.com"
]

socket.setdefaulttimeout(10)

print("=== KIỂM TRA TRẠNG THÁI WEBSITE ===")
for site in sites:
    print(f"\nChecking: {site}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(site, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string.strip() if soup.title else "No Title"
            print(f"  ✅ Trạng thái: {status} OK")
            print(f"  📝 Tiêu đề: {title}")
    except urllib.error.HTTPError as e:
        print(f"  ❌ Lỗi HTTP: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        print(f"  ❌ Lỗi kết nối: {e.reason}")
    except Exception as e:
        print(f"  ⚠️ Lỗi khác: {e}")
