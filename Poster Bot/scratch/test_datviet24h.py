import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Test datviet24h.com.vn
        url = "https://datviet24h.com.vn/dang-tin.html"
        print(f"Navigating to {url} ...")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            time.sleep(2)
            print("Current URL:", page.url)
            
            # Check for input elements with typical IDs
            has_tieude = page.locator("#tieude").count() > 0
            has_loaitin = page.locator("#loaitin").count() > 0
            has_loaibds = page.locator("#loaibds").count() > 0
            
            print(f"Form matches CMS template: #tieude={has_tieude}, #loaitin={has_loaitin}, #loaibds={has_loaibds}")
            
            # Screenshot
            page.screenshot(path="scratch/datviet24h.png")
            print("Screenshot saved.")
        except Exception as e:
            print("Failed to inspect:", e)
            
        browser.close()

if __name__ == '__main__':
    inspect()
