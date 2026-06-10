import os
import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Đang truy cập trang chủ thuviennhadat.vn...")
        page.goto("https://thuviennhadat.vn", wait_until="domcontentloaded")
        time.sleep(2)
        
        print("Đang chạy JS AJAX để login với 84935723727...")
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
        time.sleep(4)
        
        print(f"URL hiện tại: {page.url}")
        
        page.screenshot(path="thuviennhadat_ajax_login.png", full_page=True)
        print("Đã chụp màn hình thuviennhadat_ajax_login.png")
        
        browser.close()

if __name__ == "__main__":
    inspect()
