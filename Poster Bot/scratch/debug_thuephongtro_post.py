import os
import time
from playwright.sync_api import sync_playwright

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    session_dir = os.path.join(base_dir, "browser_sessions")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            headless=False,
            channel="chrome" if os.path.exists("/Applications/Google Chrome.app") else None
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Check login first
        print("Checking homepage state...")
        page.goto("https://thuephongtro.com/", wait_until="networkidle")
        time.sleep(2)
        
        print("Goto dang-tin.html...")
        page.goto("https://thuephongtro.com/dang-tin.html", wait_until="networkidle")
        time.sleep(5)
        
        print(f"URL: {page.url}")
        page.screenshot(path="thuephongtro_dangtin_page.png")
        
        inputs = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
                tag: el.tagName,
                id: el.id,
                name: el.name,
                placeholder: el.placeholder || '',
                type: el.type || ''
            }));
        }""")
        print("Form elements on thuephongtro dang-tin:")
        for inp in inputs:
            print(inp)
            
        browser.close()

if __name__ == "__main__":
    main()
