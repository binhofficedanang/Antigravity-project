import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        # Test qttv
        url = "https://dangtinbatdongsan.vn/qttv"
        print(f"Navigating to {url} ...")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            time.sleep(2)
            print("Current URL:", page.url)
            inputs = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('input, select, button, textarea')).map(el => ({
                    tag: el.tagName,
                    id: el.getAttribute('id') || '',
                    name: el.getAttribute('name') || '',
                    type: el.getAttribute('type') || '',
                    placeholder: el.getAttribute('placeholder') || ''
                }));
            }""")
            for inp in inputs:
                print(f"  {inp['tag']}: id='{inp['id']}', name='{inp['name']}', type='{inp['type']}'")
        except Exception as e:
            print("Failed:", e)
            
        browser.close()

if __name__ == '__main__':
    inspect()
