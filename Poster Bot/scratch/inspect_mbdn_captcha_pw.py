from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://muabandanang.vn/dang-ky", timeout=30000)
            page.wait_for_timeout(3000)
            
            # Extract captcha text
            captcha_html = page.evaluate("""() => {
                const el = document.querySelector('#captcha');
                if (el) {
                    return el.parentElement.innerHTML;
                }
                return 'Not found';
            }""")
            print("Captcha Parent HTML Content:\n", captcha_html)
        except Exception as e:
            print("Error:", e)
        browser.close()

if __name__ == "__main__":
    inspect()
