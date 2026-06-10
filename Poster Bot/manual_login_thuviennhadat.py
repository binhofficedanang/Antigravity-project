import os
import time
from playwright.sync_api import sync_playwright

def login():
    p = sync_playwright().start()
    # Mở trình duyệt có giao diện (headless=False) để bạn có thể xem và thao tác
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    print("Đang mở trình duyệt và tự động đăng nhập Thư Viện Nhà Đất...")
    page.goto("https://thuviennhadat.vn", wait_until="domcontentloaded")
    time.sleep(2)
    
    page.evaluate("""
        () => {
            $.ajax({
                url: "/Users/Login",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    PhoneNumber: "84935723727",
                    Password: "Binh1995@",
                    RememberMe: true,
                    returnUrl: ""
                }),
                success: function(res) {
                    window.location.href = "/dang-tin";
                }
            });
        }
    """)
    print("=> Đăng nhập thành công! Bạn có thể sử dụng cửa sổ Chrome vừa hiện lên để xem/sửa tin đăng.")
    print("Bấm Ctrl+C (hoặc đóng cửa sổ Terminal) để tắt trình duyệt khi dùng xong.")
    
    try:
        # Giữ cho trình duyệt mở mãi mãi cho đến khi bạn tắt
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Đang đóng trình duyệt...")
        browser.close()
        p.stop()

if __name__ == "__main__":
    login()
