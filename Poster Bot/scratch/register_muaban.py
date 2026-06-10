#!/usr/bin/env python3
"""
Interactive registration script for muaban.net
Opens a non-headless browser to bypass Cloudflare and allow user to register.
"""
import time
import sys
import json
import os
from playwright.sync_api import sync_playwright

CONFIG_PATH = "config.json"
PHONE = "0935723727"
EMAIL = "binh.officedanang@gmail.com"
PASSWORD = "Binh1995@"
NAME = "Nguyễn Ngọc Thiên Bình"

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def main():
    print("==================================================")
    print("HƯỚNG DẪN ĐĂNG KÝ TÀI KHOẢN MUABAN.NET:")
    print(f"- Số điện thoại đăng ký: {PHONE}")
    print(f"- Email đăng ký: {EMAIL}")
    print(f"- Mật khẩu đăng ký: {PASSWORD}")
    print("==================================================")
    
    with sync_playwright() as p:
        print("Đang khởi động trình duyệt có giao diện (non-headless)...")
        # Launch with custom arguments to bypass bot detection
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.new_page()
        
        print("Đang truy cập trang đăng ký: https://muaban.net/dang-ky ...")
        page.goto("https://muaban.net/dang-ky", timeout=60000)
        
        print("\n[HỆ THỐNG] VUI LÒNG THEO DÕI TRÌNH DUYỆT CHROME ĐANG MỞ:")
        print("1. Nếu trang hiển thị kiểm tra bảo mật (Cloudflare), bạn có thể click xác minh hoặc để nó tự chạy.")
        print("2. Sau khi vượt qua Cloudflare, hãy nhập thông tin đăng ký:")
        print(f"   - Số điện thoại: {PHONE}")
        print(f"   - Mật khẩu: {PASSWORD}")
        print("3. Nhận mã OTP gửi về điện thoại, nhập vào trang web để hoàn tất đăng ký.")
        print("4. Khi đã đăng ký thành công và trình duyệt chuyển sang trạng thái đã đăng nhập, quay lại đây và nhấn Enter.")
        
        # Let's see if we can find any inputs to autofill to help the user
        autofilled = False
        for i in range(120): # Check for up to 2 minutes
            if page.is_closed():
                print("Trình duyệt đã bị đóng.")
                break
                
            try:
                # Let's check if the standard muaban inputs are visible
                # Muaban registration form usually has text/tel inputs
                tel_inputs = page.locator("input[type='tel'], input[placeholder*='Số điện thoại'], input[name='phone'], input[name='username']")
                if tel_inputs.count() > 0 and tel_inputs.first.is_visible() and not autofilled:
                    print("\n[HỆ THỐNG] Đã phát hiện form đăng ký! Đang tự động điền thông tin giúp bạn...")
                    tel_inputs.first.fill(PHONE)
                    
                    # Fill password if visible
                    pass_inputs = page.locator("input[type='password'], input[placeholder*='mật khẩu'], input[name='password']")
                    if pass_inputs.count() > 0 and pass_inputs.first.is_visible():
                        pass_inputs.first.fill(PASSWORD)
                        
                    print("[HỆ THỐNG] Đã tự động điền Số điện thoại và Mật khẩu. Bạn chỉ cần nhập mã OTP và hoàn tất đăng ký!")
                    autofilled = True
            except Exception as e:
                pass
                
            time.sleep(1)
            
        # Ask user for confirmation
        input("\n[HỆ THỐNG] Sau khi bạn đã hoàn tất đăng ký thành công trên trình duyệt, nhấn [ENTER] tại đây để lưu cấu hình...")
        
        # Save to config.json
        print("Đang lưu thông tin tài khoản muaban.net vào file cấu hình config.json...")
        config = load_config()
        config["muaban.net"] = {
            "username": PHONE,
            "email": EMAIL,
            "password": PASSWORD,
            "phone": PHONE
        }
        save_config(config)
        print("✅ Lưu cấu hình thành công!")
        
        # Let's take a final screenshot before closing
        try:
            page.screenshot(path="scratch/muaban_registered_success.png")
            print("Đã chụp ảnh màn hình lưu tại scratch/muaban_registered_success.png")
        except Exception:
            pass
            
        print("Đang đóng trình duyệt...")
        browser.close()

if __name__ == "__main__":
    main()
