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
        
        print("Logging in...")
        page.goto("https://chothuenha.com.vn/dang-nhap", wait_until="networkidle")
        page.fill("input#login_input_telephone", "0935723727")
        page.fill("input#login_input_password", "Binh1995@")
        
        # Click login button
        page.click("button.btn_nut")
        time.sleep(5)
        print(f"URL after login: {page.url}")
        
        print("Goto tai-khoan/dang-tin...")
        page.goto("https://chothuenha.com.vn/tai-khoan/dang-tin", wait_until="networkidle")
        time.sleep(5)
        print(f"URL: {page.url}")
        page.screenshot(path="chothuenha_dangtin_page_real.png")
        
        inputs = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
                tag: el.tagName,
                id: el.id,
                name: el.name,
                placeholder: el.placeholder || '',
                type: el.type || ''
            }));
        }""")
        print("Form elements on chothuenha post page:")
        for inp in inputs:
            if inp['name'] or inp['id']:
                print(inp)
                
        browser.close()

if __name__ == "__main__":
    main()
