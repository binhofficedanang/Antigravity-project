import requests
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scan():
    url = "https://www.maumau.vn/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    print(f"Scanning {url}...")
    try:
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        print("Status code:", r.status_code)
        print("Response headers:", r.headers)
        
        server = r.headers.get("Server", "").lower()
        print("Server Header:", r.headers.get("Server"))
        
        html = r.text.lower()
        
        # Check Cloudflare
        cf = "cloudflare" in server or "cf-ray" in r.headers or any(p in html for p in ["__cf_chl_", "cloudflare-challenge", "challenge-form"])
        print("Cloudflare detected:", cf)
        
        # Check Captcha
        captcha_patterns = [
            r"recaptcha/api\.js",
            r"hcaptcha\.com",
            r"g-recaptcha",
            r"class=\"h-captcha\"",
            r"turnstile",
            r"sec-cpt",
            r"captcha-container",
            r"client-captcha"
        ]
        captcha = any(re.search(pat, html) for pat in captcha_patterns)
        print("Captcha patterns detected:", captcha)
        
        # Let's search for login link or form
        login_links = re.findall(r'href=["\']([^"\']*(?:login|dang-nhap|log-in|account)[^"\']*)["\']', html)
        print("Sample potential login links found in HTML:")
        for link in set(login_links[:10]):
            print(f"  {link}")
            
    except Exception as e:
        print("Error during scan:", e)

if __name__ == '__main__':
    scan()
