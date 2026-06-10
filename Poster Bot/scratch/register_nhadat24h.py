import time
import sys
from playwright.sync_api import sync_playwright

# Thông tin đăng ký mẫu của bạn
FULL_NAME = "Nguyễn Ngọc Thiên Bình"
EMAIL = "binh.officedanang@gmail.com"
PASSWORD = "Binh1995@"
PHONE = "0935723727"

def main():
    print("=== BẮT ĐẦU HỖ TRỢ ĐĂNG KÝ TÀI KHOẢN NHADAT24H.NET ===")
    print("Trình duyệt Chromium sẽ mở ra trực tiếp trên màn hình của bạn.")
    print("Bot sẽ điền sẵn Họ tên, Email, Mật khẩu, Số điện thoại.")
    print("Bạn chỉ cần giải Captcha và bấm nút Đăng ký, sau đó xác nhận mã OTP/Email nếu có.")
    print("-" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Mở trang đăng ký thành viên nhadat24h
        print("Đang truy cập trang đăng ký...")
        page.goto("https://nhadat24h.net/dang-ky", wait_until="domcontentloaded")
        time.sleep(3)

        if "dang-ky" not in page.url and "DKTV" not in page.url:
            page.goto("https://nhadat24h.net/DKTV-DT", wait_until="domcontentloaded")
            time.sleep(3)

        # Điền thông tin đăng ký
        print("Đang tự động điền thông tin đăng ký vào form...")
        
        # Họ tên
        for sel in ["input#txtHT", "input[name*='HT']", "input[placeholder*='Họ tên']"]:
            try:
                if page.locator(sel).count() > 0:
                    page.fill(sel, FULL_NAME)
                    break
            except:
                pass

        # Email
        for sel in ["input#txtEmail", "input[name*='Email']", "input[placeholder*='Email']"]:
            try:
                if page.locator(sel).count() > 0:
                    page.fill(sel, EMAIL)
                    break
            except:
                pass

        # Mật khẩu
        for sel in ["input#txtMatKhau", "input#txtMatKhau1", "input[type='password']"]:
            try:
                if page.locator(sel).count() > 0:
                    page.fill(sel, PASSWORD)
                    break
            except:
                pass

        # Số điện thoại
        for sel in ["input#Mobile", "input#txtMobile", "input#txtPhone", "input[placeholder*='điện thoại']"]:
            try:
                if page.locator(sel).count() > 0:
                    page.fill(sel, PHONE)
                    break
            except:
                pass

        print("\n✅ Đã điền xong thông tin!")
        print("👉 Vui lòng giải Captcha trên màn hình Chromium vừa hiện ra và nhấn nút Đăng ký.")
        print("Sau khi hoàn thành, vui lòng để nguyên hoặc tắt trình duyệt. Bot sẽ tự động đóng sau 3 phút.")
        print("-" * 60)

        # Giữ trình duyệt mở trong 180 giây để người dùng thao tác
        for i in range(18, 0, -1):
            time.sleep(10)
            print(f"Trình duyệt đang mở... (Tự đóng sau {i * 10} giây nữa)")

        browser.close()
        print("=== KẾT THÚC ===")

if __name__ == "__main__":
    main()
