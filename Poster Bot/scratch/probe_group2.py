import requests
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

domains = [
    "chototnhadat.vn", "nhapho24h.vn", "tinbds.com", "dangtinbds.com",
    "dangtinbatdongsan.com", "dangtinmienphi.vn", "raovatbds.vn",
    "chotot.info", "bds24h.com", "batdongsangiatot.com.vn", "chonhadat24h.com",
    "dangtinbatdongsan.vn"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

print("Checking proposed Group 2 sites for template similarities and active status...")
for domain in domains:
    url = f"https://{domain}"
    try:
        res = requests.get(url, headers=headers, timeout=5, verify=False, allow_redirects=True)
        html = res.text.lower()
        
        # Check if the clone signature exists (e.g. references to 123nhadatviet or specific css/js or input fields)
        is_clone = False
        if "txtusername" in html or "txtpassword" in html or "txtemail" in html or "dang-nhap.html" in html:
            is_clone = True
            
        print(f"{domain:25} | Status: {res.status_code} | Is Clone Sign: {is_clone} | Size: {len(res.text)}")
    except Exception as e:
        # try http
        try:
            url = f"http://{domain}"
            res = requests.get(url, headers=headers, timeout=5, verify=False, allow_redirects=True)
            html = res.text.lower()
            is_clone = False
            if "txtusername" in html or "txtpassword" in html or "txtemail" in html or "dang-nhap.html" in html:
                is_clone = True
            print(f"{domain:25} | Status: {res.status_code} (HTTP) | Is Clone Sign: {is_clone} | Size: {len(res.text)}")
        except Exception as e2:
            print(f"{domain:25} | FAILED: {str(e2)[:50]}")
