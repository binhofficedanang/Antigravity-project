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
        
        print("Chuyển sang tab Đăng ký...")
        page.click("#register-view")
        time.sleep(2)
        
        print("Nhập số điện thoại đăng ký: 0935723727")
        page.fill("input#phone-regist-view", "0935723727")
        
        # Click tiếp tục
        print("Click Tiếp tục (bước 1)...")
        page.click("button#button-submit-regist-view")
        time.sleep(4)
        
        # Điền mật khẩu
        print("Điền mật khẩu: Binh1995@...")
        page.fill("input#password-regist-view", "Binh1995@")
        page.fill("input#confirm-password-regist-view", "Binh1995@")
        time.sleep(1)
        
        # Chụp ảnh trước khi click
        page.screenshot(path="thuviennhadat_register_filled.png")
        print("Đã chụp ảnh trước khi click vào thuviennhadat_register_filled.png")
        
        # Click hoàn tất
        print("Click Tiếp tục (bước 2) để đăng ký...")
        page.click("button#button-submit-verify-password-view")
        time.sleep(8)
        
        print(f"URL sau khi click: {page.url}")
        
        # Chụp ảnh sau khi click
        page.screenshot(path="thuviennhadat_register_clicked.png")
        print("Đã chụp ảnh sau khi click vào thuviennhadat_register_clicked.png")
        
        browser.close()

if __name__ == "__main__":
    main()
