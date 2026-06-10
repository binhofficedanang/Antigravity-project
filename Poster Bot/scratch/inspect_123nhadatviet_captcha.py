import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://123nhadatviet.com/dang-tin.html")
        time.sleep(3)
        
        # Get outer HTML of captcha input and its surrounding parent elements
        captcha_html = page.evaluate("""() => {
            const el = document.querySelector('input[name="captcha"]');
            if (!el) return 'Captcha input not found';
            // get parent div or row
            let parent = el.parentElement;
            for (let i = 0; i < 3; i++) {
                if (parent && parent.parentElement) {
                    parent = parent.parentElement;
                }
            }
            return parent ? parent.outerHTML : el.outerHTML;
        }""")
        print("Surrounding Captcha HTML:")
        print(captcha_html)
        
        browser.close()

if __name__ == "__main__":
    inspect()
