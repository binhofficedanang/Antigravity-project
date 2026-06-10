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
        
        print("Goto dang-nhap.html page...")
        page.goto("https://thuephongtro.com/dang-nhap.html", wait_until="networkidle")
        time.sleep(2)
        
        page.fill("input#Email", "binh.officedanang@gmail.com")
        page.fill("input#Password", "Binh1995@")
        
        print("Clicking submit...")
        page.click("button[type='submit']")
        time.sleep(5)
        
        print(f"URL: {page.url}")
        body_text = page.evaluate("() => document.body.innerText")
        print("Body Text containing error?")
        print([line for line in body_text.split('\n') if 'sai' in line.lower() or 'mật khẩu' in line.lower() or 'không' in line.lower()][:10])
        
        browser.close()

if __name__ == "__main__":
    main()
