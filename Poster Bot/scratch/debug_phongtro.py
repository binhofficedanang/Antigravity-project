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
        
        print("Goto phongtro123 homepage...")
        page.goto("https://phongtro123.com/", wait_until="domcontentloaded")
        time.sleep(3)
        
        # Click the "Đăng tin" button
        try:
            dangtin_btn = page.locator("a:has-text('Đăng tin'), .btn-orange").first
            if dangtin_btn.is_visible():
                print("Clicking 'Đăng tin' button...")
                dangtin_btn.click()
                time.sleep(5)
                print(f"URL after clicking: {page.url}")
                page.screenshot(path="phongtro123_after_click.png")
            else:
                print("Could not find 'Đăng tin' button.")
        except Exception as e:
            print(f"Error clicking button: {e}")
            
        browser.close()

if __name__ == "__main__":
    main()
