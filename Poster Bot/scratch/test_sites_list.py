import time
from playwright.sync_api import sync_playwright

def inspect():
    sites = [
        "nhadat247.net",
        "raovat247.net",
        "nhadat24h.net",
        "chonhadat24h.com",
        "dangtinbatdongsan.vn"
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        for site in sites:
            url = f"http://{site}/dang-tin.html"
            print(f"Checking {url} ...")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=8000)
                time.sleep(1.5)
                has_tieude = page.locator("#tieude").count() > 0
                has_loaitin = page.locator("#loaitin").count() > 0
                has_loaibds = page.locator("#loaibds").count() > 0
                print(f"  Result: #tieude={has_tieude}, #loaitin={has_loaitin}, #loaibds={has_loaibds}")
            except Exception as e:
                print(f"  Failed: {e}")
                
        browser.close()

if __name__ == '__main__':
    inspect()
