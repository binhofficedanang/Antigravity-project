import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        # 1. datviet24h.com.vn login inputs
        print("\n--- datviet24h.com.vn login form ---")
        try:
            page.goto("https://datviet24h.com.vn/dang-nhap.html", wait_until="domcontentloaded")
            time.sleep(2)
            inputs = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('input, select, button')).map(el => ({
                    tag: el.tagName,
                    id: el.getAttribute('id') || '',
                    name: el.getAttribute('name') || '',
                    type: el.getAttribute('type') || ''
                }));
            }""")
            for inp in inputs:
                print(f"  {inp['tag']}: id='{inp['id']}', name='{inp['name']}', type='{inp['type']}'")
        except Exception as e:
            print("  Failed:", e)
            
        # 2. luachonnhadat.vn login inputs
        print("\n--- luachonnhadat.vn login form ---")
        try:
            page.goto("https://luachonnhadat.vn/dang-nhap.html", wait_until="domcontentloaded")
            time.sleep(2)
            inputs = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('input, select, button')).map(el => ({
                    tag: el.tagName,
                    id: el.getAttribute('id') || '',
                    name: el.getAttribute('name') || '',
                    type: el.getAttribute('type') || ''
                }));
            }""")
            for inp in inputs:
                print(f"  {inp['tag']}: id='{inp['id']}', name='{inp['name']}', type='{inp['type']}'")
        except Exception as e:
            print("  Failed:", e)
            
        # 3. dangtinbatdongsan.vn check
        print("\n--- dangtinbatdongsan.vn homepage check ---")
        try:
            r = page.goto("http://dangtinbatdongsan.vn/", wait_until="domcontentloaded", timeout=10000)
            print(f"  Status code: {r.status}")
            print(f"  Current URL: {page.url}")
        except Exception as e:
            print("  Failed:", e)
            
        # 4. diaocanphu.com check
        print("\n--- diaocanphu.com login inputs ---")
        try:
            page.goto("http://diaocanphu.com/dang-nhap.html", wait_until="domcontentloaded")
            time.sleep(2)
            inputs = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('input, select, button')).map(el => ({
                    tag: el.tagName,
                    id: el.getAttribute('id') || '',
                    name: el.getAttribute('name') || '',
                    type: el.getAttribute('type') || ''
                }));
            }""")
            for inp in inputs:
                print(f"  {inp['tag']}: id='{inp['id']}', name='{inp['name']}', type='{inp['type']}'")
        except Exception as e:
            print("  Failed:", e)
            
        browser.close()

if __name__ == '__main__':
    inspect()
