import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://123nhadatviet.com/dang-tin.html")
        time.sleep(3)
        
        # Get outer HTML of price input and surrounding elements
        price_html = page.evaluate("""() => {
            const el = document.getElementById('gia');
            if (!el) return 'Price input not found';
            let parent = el.parentElement;
            for (let i = 0; i < 2; i++) {
                if (parent && parent.parentElement) {
                    parent = parent.parentElement;
                }
            }
            return parent ? parent.outerHTML : el.outerHTML;
        }""")
        print("Surrounding Price HTML:")
        print(price_html)
        
        browser.close()

if __name__ == "__main__":
    inspect()
