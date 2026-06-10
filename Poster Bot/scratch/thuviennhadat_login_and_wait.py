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
        
        print("Điền tài khoản...")
        page.fill("input#phone-mail-login-view", "0935723727")
        page.fill("input#password-login-view", "Binh1995@")
        
        print("Click Đăng nhập...")
        page.click("button#button-submit-login-view")
        
        # Chờ chuyển hướng sang trang đăng tin
        print("Chờ chuyển hướng sang dang-tin...")
        try:
            page.wait_for_url("**/dang-tin", timeout=15000)
            print("Đã chuyển hướng sang dang-tin thành công!")
        except Exception as e:
            print("Lỗi khi chờ chuyển hướng:", e)
            
        print(f"URL hiện tại: {page.url}")
        
        # Chụp màn hình sau khi đăng nhập
        page.screenshot(path="thuviennhadat_after_login.png")
        print("Đã chụp ảnh thuviennhadat_after_login.png")
        
        browser.close()

if __name__ == "__main__":
    main()
