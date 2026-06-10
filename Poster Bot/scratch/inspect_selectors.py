import requests
from bs4 import BeautifulSoup

url = "https://propertydanang.com/property/toa-nha-vietinbank/"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    print("=== EVERY ELEMENT WITH CLASS CONTAINING 'address' ===")
    for el in soup.find_all(class_=True):
        classes = el.get('class')
        class_str = " ".join(classes)
        if 'address' in class_str:
            print(f"Class: {class_str} | Tag: {el.name} | Text: {el.get_text().strip()}")
            
    print("\n=== EVERY ELEMENT WITH CLASS CONTAINING 'price' ===")
    for el in soup.find_all(class_=True):
        classes = el.get('class')
        class_str = " ".join(classes)
        if 'price' in class_str:
            print(f"Class: {class_str} | Tag: {el.name} | Text: {el.get_text().strip()}")

    print("\n=== EVERY ELEMENT WITH CLASS CONTAINING 'area' ===")
    for el in soup.find_all(class_=True):
        classes = el.get('class')
        class_str = " ".join(classes)
        if 'area' in class_str:
            print(f"Class: {class_str} | Tag: {el.name} | Text: {el.get_text().strip()}")

    print("\n=== INSPECTING THE DETAIL PAGE CONTENT STRUCTURE ===")
    # Tìm thẻ chứa mô tả chính
    # Thông thường WordPress post content nằm trong div có class entry-content hoặc single-property, v.v.
    # Hãy in các div lớn chứa nhiều chữ
    for el in soup.find_all("div", class_=True):
        c = " ".join(el.get('class'))
        txt = el.get_text().strip()
        if len(txt) > 500 and ('content' in c or 'desc' in c or 'detail' in c or 'property' in c or 'summary' in c):
            print(f"Large Div Class: {c} | Tag: {el.name} | Text preview: {txt[:200]}...")
            print("-" * 50)
            
except Exception as e:
    print(f"Error: {e}")
