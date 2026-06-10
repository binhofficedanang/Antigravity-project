#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from playwright.sync_api import sync_playwright

def main():
    sites = [
        "raovatnhadat.org",
        "muabannhadat.top",
        "batdongsan247.net"
    ]
    
    user_details = {
        "fullname": "Nguyễn Ngọc Thiên Bình",
        "username": "binhofficedanang",
        "email": "binh.officedanang@gmail.com",
        "phone": "0935723727",
        "password": "Binh1995@"
    }
    
    print("🚀 Bắt đầu trình tự tự động đăng ký tài khoản trên các trang clone còn lại...")
    print("💡 Trình duyệt sẽ mở ra, tự điền toàn bộ thông tin đăng ký.")
    print("💡 Bạn chỉ cần nhập mã CAPTCHA hình ảnh (nếu có) và nhấn nút Đăng ký.")
    print("💡 Sau khi hoàn thành xong 1 trang, hãy nhắn 'tiếp tục' ở đây để chuyển trang.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome" if os.path.exists("/Applications/Google Chrome.app") else None,
            args=["--start-maximized"]
        )
        
        context = browser.new_context(viewport=None)
        page = context.new_page()
        
        for site in sites:
            print(f"\n🌐 [Trang: {site}]...")
            url = f"http://{site}/dang-ky.html"
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                time.sleep(2)
                
                # Điền form thông minh
                fields = {
                    "username": ["input#username", "input[name='username']", "input#user", "input[name='user']"],
                    "fullname": ["input#fullname", "input[name='fullname']", "input#hoten", "input[name='hoten']", "input#name", "input[name='name']"],
                    "email": ["input#email", "input[name='email']", "input#txtEmail", "input[name='txtEmail']"],
                    "phone": ["input#phone", "input[name='phone']", "input#dienthoai", "input[name='dienthoai']", "input#txtPhone", "input[name='txtPhone']"],
                    "password": ["input#password", "input[name='password']", "input#txtPassword", "input[name='txtPassword']"],
                    "repassword": ["input#repassword", "input[name='repassword']", "input#re_password", "input[name='re_password']", "input#txtConfirmPassword", "input[name='txtConfirmPassword']"]
                }
                
                for key, selectors in fields.items():
                    val = user_details.get(key)
                    if key == "repassword":
                        val = user_details.get("password")
                    
                    filled = False
                    for sel in selectors:
                        try:
                            loc = page.locator(sel)
                            if loc.count() > 0 and loc.first.is_visible():
                                loc.first.fill(val)
                                filled = True
                                break
                        except Exception:
                            continue
                    if filled:
                        print(f"  ✓ Đã điền: {key}")
                
                print("👉 Vui lòng nhập CAPTCHA và click 'Đăng ký' trên giao diện Chrome.")
                input("⌨️  Sau khi click đăng ký thành công, hãy nhấn ENTER tại đây để sang trang tiếp theo...")
                
            except Exception as e:
                print(f"  ❌ Lỗi khi tải trang {site}: {e}")
                input("⌨️  Nhấn ENTER để bỏ qua trang này và tiếp tục...")
        
        browser.close()
        print("\n🏁 Đã hoàn thành toàn bộ danh sách đăng ký!")

if __name__ == "__main__":
    main()
