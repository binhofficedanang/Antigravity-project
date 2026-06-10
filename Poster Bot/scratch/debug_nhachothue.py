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
        
        print("Goto nhachothue homepage...")
        page.goto("https://nhachothue.vn/", wait_until="networkidle")
        time.sleep(5)
        
        # Search for registration/login links
        links = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a')).map(el => ({
                text: el.innerText || '',
                href: el.href || ''
            })).filter(item => item.text.toLowerCase().includes('đăng') || item.text.toLowerCase().includes('login') || item.href.includes('dang-') || item.href.includes('login'));
        }""")
        print("Relevant links on nhachothue.vn homepage:")
        for link in links:
            print(link)
            
        browser.close()

if __name__ == "__main__":
    main()
