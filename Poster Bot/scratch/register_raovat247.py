import time
from playwright.sync_api import sync_playwright

# Thông tin mẫu
USERNAME = "binh.officedanang"
EMAIL = "binh.officedanang@gmail.com"
PASSWORD = "Binh1995@"

def main():
    print("=== BẮT ĐẦU HỖ TRỢ ĐĂNG KÝ TÀI KHOẢN RAOVAT247.NET ===")
    print("Trình duyệt Chromium sẽ mở ra trực tiếp trên màn hình của bạn.")
    print("Bot sẽ điền sẵn Tên đăng nhập, Email, Mật khẩu.")
    print("Bạn chỉ cần giải Captcha và bấm nút Đăng ký, sau đó xác nhận email.")
    print("-" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Mở trang đăng ký
        print("Đang truy cập trang đăng ký...")
        page.goto("https://raovat247.net/register/", wait_until="domcontentloaded")
        time.sleep(3)

        # Điền form
        print("Đang tự động điền thông tin đăng ký...")
        try:
            page.fill("input[name='username']", USERNAME)
        except Exception as e:
            print("  ⚠️ Không điền được username:", e)

        try:
            page.fill("input[name='email']", EMAIL)
        except Exception as e:
            print("  ⚠️ Không điền được email:", e)

        try:
            page.fill("input[name='password']", PASSWORD)
        except Exception as e:
            print("  ⚠️ Không điền được password:", e)

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
