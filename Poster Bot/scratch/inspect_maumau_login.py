import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = "https://id.maumau.vn/login?return-url=https%3A%2F%2Fmaumau.vn&code=maumau"
        print(f"Navigating to {url} ...")
        page.goto(url, wait_until="networkidle")
        time.sleep(3)
        
        print("Page URL:", page.url)
        print("Page Title:", page.title())
        
        # Save screenshot
        page.screenshot(path="scratch/maumau_login.png", full_page=True)
        print("Saved login screenshot to scratch/maumau_login.png")
        
        # Find all inputs
        inputs = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('input, select, textarea, button')).map(el => ({
                tag: el.tagName,
                type: el.getAttribute('type') || '',
                id: el.getAttribute('id') || '',
                name: el.getAttribute('name') || '',
                placeholder: el.getAttribute('placeholder') || '',
                value: el.value || ''
            }));
        }""")
        
        print(f"Found {len(inputs)} input elements:")
        for idx, inp in enumerate(inputs):
            print(f"  [{idx}] {inp['tag']}: id='{inp['id']}', name='{inp['name']}', type='{inp['type']}', placeholder='{inp['placeholder']}'")
            
        browser.close()

if __name__ == '__main__':
    inspect()
