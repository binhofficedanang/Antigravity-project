import time
import random
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print("Đang mở trang đăng nhập trực tiếp...")
        page.goto("https://thuviennhadat.vn/Users/Login?returnUrl=%2Fdang-tin", wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)
        
        # Nhấp vào Đăng ký sử dụng ID
        print("Nhấp vào liên kết Đăng ký (#register-view)...")
        page.click("#register-view")
        time.sleep(3)
        
        # Nhập số điện thoại ngẫu nhiên
        phone_num = "098" + "".join([str(random.randint(0, 9)) for _ in range(7)])
        print(f"Nhập số điện thoại đăng ký: {phone_num}")
        page.fill("input#phone-mail-login", phone_num)
        
        # Submit số điện thoại
        page.click("button#button-submit-login")
        time.sleep(3)
        
        # Điền mật khẩu
        password = "Password123@"
        print(f"Điền mật khẩu: {password}")
        page.fill("input#password-login", password)
        page.fill("input#repassword-login", password)
        
        # Click đăng ký hoàn tất
        page.click("button#button-submit-login")
        time.sleep(5)
        
        print("Đang kiểm tra xem đã chuyển đến trang Đăng tin chưa...")
        print(f"URL hiện tại: {page.url}")
        
        # Nếu chưa chuyển trang, hãy tự chuyển hướng sang /dang-tin
        if "dang-tin" not in page.url:
            page.goto("https://thuviennhadat.vn/dang-tin", wait_until="domcontentloaded")
            time.sleep(5)
            
        print(f"URL cuối cùng: {page.url}")
        
        # Lưu HTML trang đăng tin để phân tích selectors
        html_content = page.content()
        with open("thuviennhadat_dangtin.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Đã lưu cấu trúc HTML trang Đăng tin thành công vào thuviennhadat_dangtin.html")
        
        # Chụp màn hình trang đăng tin để xem giao diện
        page.screenshot(path="thuviennhadat_dangtin.png")
        print("Đã chụp màn hình trang Đăng tin vào thuviennhadat_dangtin.png")
        
        browser.close()

if __name__ == "__main__":
    main()
