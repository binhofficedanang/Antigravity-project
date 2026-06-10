import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print("Đang mở trang đăng nhập...")
        page.goto("https://thuviennhadat.vn/Users/Login?returnUrl=%2Fdang-tin", wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)
        
        # Thử đăng nhập bằng số 84935723727
        print("Điền tài khoản: 84935723727...")
        page.fill("input#phone-mail-login-view", "84935723727")
        page.fill("input#password-login-view", "Binh1995@")
        
        print("Click Đăng nhập...")
        page.click("button#button-submit-login-view")
        time.sleep(6)
        
        print(f"URL hiện tại: {page.url}")
        
        # Chụp màn hình
        page.screenshot(path="thuviennhadat_login_84.png")
        print("Đã chụp ảnh kết quả vào thuviennhadat_login_84.png")
        
        browser.close()

if __name__ == "__main__":
    main()
