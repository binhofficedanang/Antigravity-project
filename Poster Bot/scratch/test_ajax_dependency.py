import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://123nhadatviet.com/dang-tin.html")
        time.sleep(3)
        
        # Select city: 3 (Đà Nẵng) and huyen: 584 (Hải Châu)
        page.select_option("#tinh", "3")
        time.sleep(2)
        page.select_option("#huyen", "584")
        time.sleep(2)
        
        # Let's see street count for district first
        streets_all = page.evaluate("""() => {
            return Array.from(document.getElementById('duong').options).map(o => o.text);
        }""")
        print("Total streets for District Hải Châu:", len(streets_all))
        
        # Select ward Bình Hiên (1088)
        print("Selecting Phường Bình Hiên (1088)...")
        page.evaluate("() => { const el = document.getElementById('phuong'); el.value = '1088'; el.dispatchEvent(new Event('change')); }")
        time.sleep(1.5)
        
        # Check street count
        streets_binhhien = page.evaluate("""() => {
            return Array.from(document.getElementById('duong').options).map(o => o.text);
        }""")
        print("Streets under Phường Bình Hiên:", len(streets_binhhien))
        print("Sample streets:", streets_binhhien[:10])
        
        # Select ward Hòa Cường Bắc (1093)
        print("Selecting Phường Hòa Cường Bắc (1093)...")
        page.evaluate("() => { const el = document.getElementById('phuong'); el.value = '1093'; el.dispatchEvent(new Event('change')); }")
        time.sleep(1.5)
        
        # Check street count
        streets_hoacuongbac = page.evaluate("""() => {
            return Array.from(document.getElementById('duong').options).map(o => o.text);
        }""")
        print("Streets under Phường Hòa Cường Bắc:", len(streets_hoacuongbac))
        print("Sample streets:", streets_hoacuongbac[:10])
        
        browser.close()

if __name__ == '__main__':
    inspect()
