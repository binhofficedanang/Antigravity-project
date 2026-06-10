import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        # 1. datviet24h.com.vn register page
        print("\n--- datviet24h.com.vn registration ---")
        try:
            page.goto("https://datviet24h.com.vn/dang-ky.html", wait_until="domcontentloaded")
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
            
        # 2. dangtinbatdongsan.vn register page
        print("\n--- dangtinbatdongsan.vn registration ---")
        try:
            page.goto("https://dangtinbatdongsan.vn/qttv/login", wait_until="domcontentloaded")
            time.sleep(2)
            page.click("#btnDangKy")
            time.sleep(2)
            print("  Current URL after click register:", page.url)
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
            
        # 3. diaocanphu.com register page
        print("\n--- diaocanphu.com registration ---")
        try:
            page.goto("http://diaocanphu.com/dang-ky.html", wait_until="domcontentloaded")
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
