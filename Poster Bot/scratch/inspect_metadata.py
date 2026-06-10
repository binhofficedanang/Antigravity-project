import requests
from bs4 import BeautifulSoup

url = "https://propertydanang.com/property/toa-nha-vietinbank/"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # In ra toàn bộ HTML của div chứa metadata của bất động sản.
    # Thường nó nằm ở các class như property-meta-wrap, property-features, v.v.
    # Hãy tìm bất kỳ phần tử nào có chứa text "Diện tích trống" hoặc "Diện tích sàn"
    for tag in soup.find_all(True):
        if tag.string and ("Diện tích trống" in tag.string or "Diện tích sàn" in tag.string or "Năm xây dựng" in tag.string):
            print(f"Tag: {tag.name} | Text: '{tag.string.strip()}' | Parent: {tag.parent.name} | Parent classes: {tag.parent.get('class')}")
            
    print("\n=== PRINTING ALL LIST ITEMS OR DIVS UNDER THE DETAILS WRAPPER ===")
    for el in soup.find_all(class_=True):
        c = " ".join(el.get('class'))
        if any(keyword in c for keyword in ['meta', 'feature', 'info', 'detail', 'attribute', 'spec']):
            txt = el.get_text().strip()
            if len(txt) > 0 and len(txt) < 300:
                print(f"Class: {c} | Tag: {el.name} | Text: {txt}")
                
except Exception as e:
    print("Error:", e)
