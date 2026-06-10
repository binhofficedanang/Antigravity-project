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
        page.fill("input#phone-mail-login-view", "binh.officedanang@gmail.com")
        page.fill("input#password-login-view", "Binh1995@")
        
        print("Click Đăng nhập...")
        page.click("button#button-submit-login-view")
        time.sleep(5)
        
        print(f"URL hiện tại sau khi đăng nhập: {page.url}")
        
        # Chụp ảnh màn hình kết quả
        page.screenshot(path="thuviennhadat_login_result.png")
        print("Đã chụp ảnh kết quả vào thuviennhadat_login_result.png")
        
        if "dang-tin" in page.url:
            print("Đăng nhập THÀNH CÔNG và đã chuyển sang trang Đăng tin!")
            # Lưu HTML trang đăng tin
            html_content = page.content()
            with open("thuviennhadat_dangtin.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("Đã lưu HTML trang Đăng tin!")
        else:
            print("Đăng nhập THẤT BẠI hoặc chưa chuyển sang trang Đăng tin.")
            
        browser.close()

if __name__ == "__main__":
    main()
