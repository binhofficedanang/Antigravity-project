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
        
        # Điền SĐT thật của người dùng
        print("Nhập số điện thoại đăng ký: 0935723727")
        page.fill("input#phone-regist-view", "0935723727")
        
        # Click tiếp tục
        print("Click Tiếp tục (bước 1)...")
        page.click("button#button-submit-regist-view")
        time.sleep(3)
        
        # Điền mật khẩu
        print("Điền mật khẩu: Binh1995@")
        page.fill("input#password-regist-view", "Binh1995@")
        page.fill("input#confirm-password-regist-view", "Binh1995@")
        
        # Click hoàn tất đăng ký
        print("Click Tiếp tục (bước 2) để đăng ký...")
        page.click("button#button-submit-verify-password-view")
        time.sleep(8)
        
        print(f"URL hiện tại: {page.url}")
        
        # Nếu chưa tự chuyển hướng đến dang-tin, hãy chuyển hướng thủ công
        if "dang-tin" not in page.url:
            print("Đang điều hướng thủ công sang trang đăng tin...")
            page.goto("https://thuviennhadat.vn/dang-tin", wait_until="domcontentloaded")
            time.sleep(5)
            
        print(f"URL cuối cùng: {page.url}")
        
        # Lưu HTML trang đăng tin
        html_content = page.content()
        with open("thuviennhadat_dangtin.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Đã lưu cấu trúc HTML trang Đăng tin thành công vào thuviennhadat_dangtin.html")
        
        # Chụp màn hình trang đăng tin để phân tích giao diện
        page.screenshot(path="thuviennhadat_dangtin.png")
        print("Đã chụp màn hình trang Đăng tin vào thuviennhadat_dangtin.png")
        
        browser.close()

if __name__ == "__main__":
    main()
