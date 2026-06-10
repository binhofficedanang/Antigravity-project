import requests
from bs4 import BeautifulSoup

url = "https://propertydanang.com/property-type/toa-nha-cho-thue/"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # In tất cả các class liên quan đến page, pagination, v.v.
    print("=== SEARCHING HTML FOR PAGINATION RELATED ELEMENTS ===")
    for el in soup.find_all(class_=True):
        c = " ".join(el.get('class'))
        if 'page' in c or 'navi' in c or 'pagin' in c or 'pagination' in c:
            print(f"Class: {c} | Tag: {el.name} | Text: {el.get_text().strip()[:100]}")
            
except Exception as e:
    print("Error:", e)
