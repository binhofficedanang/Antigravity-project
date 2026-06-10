import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://123nhadatviet.com/dang-tin.html")
        time.sleep(3)
        
        # Get outerHTML, size, visibility, and value properties
        info = page.evaluate("""() => {
            const el = document.getElementById('noidung');
            if (!el) return 'Not found';
            return {
                html: el.outerHTML,
                value: el.value,
                visible: el.offsetWidth > 0 && el.offsetHeight > 0,
                parentHtml: el.parentElement ? el.parentElement.outerHTML : 'no parent',
                className: el.className
            };
        }""")
        import pprint
        pprint.pprint(info)
        
        browser.close()

if __name__ == "__main__":
    inspect()
