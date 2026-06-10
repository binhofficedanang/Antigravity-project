import requests
from bs4 import BeautifulSoup

url = "https://propertydanang.com/property-type/toa-nha-cho-thue/"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # 1. Trích xuất tất cả các liên kết có chứa "/property/"
    print("=== PROPERTY DETAIL LINKS ON LIST PAGE ===")
    detail_links = []
    for a in soup.find_all("a", href=True):
        href = a['href']
        if "/property/" in href and href not in detail_links:
            detail_links.append(href)
            print("Found Link:", href)
            
    # 2. Tìm liên kết phân trang (Pagination)
    print("\n=== PAGINATION LINKS ===")
    pagination = soup.select(".pagination, .page-numbers, [class*='pagination']")
    if pagination:
        for p in pagination:
            for a in p.find_all("a", href=True):
                print(f"Page Link: {a['href']} | Text: {a.get_text().strip()}")
    else:
        print("No pagination element found via standard selectors")
        # Quét chay các liên kết chứa "/page/"
        page_links = [a['href'] for a in soup.find_all("a", href=True) if "/page/" in a['href']]
        print("Page links found by scan:", set(page_links))
        
except Exception as e:
    print("Error:", e)
