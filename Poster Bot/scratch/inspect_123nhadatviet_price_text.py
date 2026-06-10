import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://123nhadatviet.com/dang-tin.html")
        time.sleep(3)
        
        # Test values: '0', '', '500', '15000', '500000', '1000000'
        test_vals = ['0', '', '500', '15000', '500000', '1000000']
        for val in test_vals:
            page.fill('#gia', val)
            page.locator('#gia').evaluate("e => e.dispatchEvent(new Event('keyup'))")
            time.sleep(0.5)
            price_text = page.inner_text('#price_text')
            print(f"Input: '{val}' => Display Text: '{price_text}'")
            
        browser.close()

if __name__ == "__main__":
    inspect()
