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
        
        # Điền mật khẩu trước
        page.fill("input#password-login-view", "Binh1995@")
        
        # Điền tài khoản bằng JS để qua mặt validator
        print("Điền tài khoản: 84935723727 bằng evaluate...")
        page.evaluate('document.querySelector("#phone-mail-login-view").value = "84935723727"')
        # Dispatch input event để đảm bảo binding hoạt động
        page.evaluate('document.querySelector("#phone-mail-login-view").dispatchEvent(new Event("input", { bubbles: true }))')
        time.sleep(1)
        
        # Chụp ảnh trước khi click
        page.screenshot(path="thuviennhadat_login_bypass_before.png")
        print("Đã chụp ảnh trước khi click vào thuviennhadat_login_bypass_before.png")
        
        print("Click Đăng nhập...")
        page.click("button#button-submit-login-view")
        time.sleep(6)
        
        print(f"URL hiện tại: {page.url}")
        
        # Chụp màn hình sau khi click
        page.screenshot(path="thuviennhadat_login_bypass.png")
        print("Đã chụp ảnh kết quả vào thuviennhadat_login_bypass.png")
        
        browser.close()

if __name__ == "__main__":
    main()
