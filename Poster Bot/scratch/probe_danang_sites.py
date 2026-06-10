import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

domains = [
    "tinraovatdanang.com", "muabandanang.vn", "danangrao.com",
    "raovatquangnam.com", "raovathue.com", "danangplus.com"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

for d in domains:
    for proto in ["https", "http"]:
        url = f"{proto}://{d}"
        try:
            res = requests.get(url, headers=headers, timeout=5, verify=False, allow_redirects=True)
            print(f"{d} -> Status: {res.status_code}, Length: {len(res.text)}, URL: {res.url}")
            break
        except Exception as e:
            print(f"{d} ({proto}) -> FAILED: {str(e)[:50]}")
