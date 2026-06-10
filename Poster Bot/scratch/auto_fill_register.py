#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
from playwright.sync_api import sync_playwright

def prompt_user(msg):
    print(f"\n👉 {msg}")
    input("👉 Nhấn Enter tại đây để tiếp tục trang tiếp theo...")

def main():
    print("🚀 Bắt đầu quá trình điền thông tin đăng ký tự động trên 4 trang Cho thuê...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    session_dir = os.path.join(base_dir, "browser_sessions")
    
    # Credentials mặc định
    fullname = "Bình Office Đà Nẵng"
    phone = "0935723727"
    email = "binh.officedanang@gmail.com"
    password = "Binh1995@"
    username = "binhofficedanang"

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=session_dir,
                headless=False,
                channel="chrome" if os.path.exists("/Applications/Google Chrome.app") else None,
                args=["--start-maximized"]
            )
            
            # --- Trang 1: phongtro123.com ---
            print("\n-------------------------------------------")
            print("1. Đang mở trang đăng ký: phongtro123.com")
            page = browser.pages[0] if browser.pages else browser.new_page()
            try:
                page.goto("https://phongtro123.com/dang-ky", timeout=30000)
                page.wait_for_load_state("networkidle")
                
                # Tự động điền
                try:
                    page.locator("input[id='user_name']").fill(fullname)
                except:
                    try: page.locator("input[placeholder*='tên']").first.fill(fullname)
                    except: pass
                
                try:
                    page.locator("input[id='user_phone']").fill(phone)
                except:
                    try: page.locator("input[placeholder*='thoại']").first.fill(phone)
                    except: pass
                
                try:
                    page.locator("input[id='user_password']").fill(password)
                except:
                    try: page.locator("input[type='password']").first.fill(password)
                    except: pass
                
                print("✅ Đã điền thông tin đăng ký phongtro123.com.")
            except Exception as e:
                print(f"⚠️ Lỗi khi mở/điền phongtro123.com: {e}")
            prompt_user("Hãy giải Captcha/nhập OTP (nếu có), hoàn tất đăng ký phongtro123.com rồi quay lại terminal.")

            # --- Trang 2: thuephongtro.com ---
            print("\n-------------------------------------------")
            print("2. Đang mở trang đăng ký: thuephongtro.com")
            try:
                page = browser.new_page()
                page.goto("https://thuephongtro.com/dang-ky", timeout=30000)
                page.wait_for_load_state("networkidle")
                
                # Tự động điền
                try:
                    page.locator("input[name*='name']").first.fill(fullname)
                except:
                    try: page.locator("input[placeholder*='tên']").first.fill(fullname)
                    except: pass
                
                try:
                    page.locator("input[name*='phone']").first.fill(phone)
                except:
                    try: page.locator("input[placeholder*='thoại']").first.fill(phone)
                    except: pass

                try:
                    page.locator("input[name*='email']").first.fill(email)
                except:
                    try: page.locator("input[placeholder*='email']").first.fill(email)
                    except: pass
                
                try:
                    page.locator("input[type='password']").first.fill(password)
                    page.locator("input[name*='password_confirmation']").first.fill(password)
                except:
                    pass
                
                print("✅ Đã điền thông tin đăng ký thuephongtro.com.")
            except Exception as e:
                print(f"⚠️ Lỗi khi mở/điền thuephongtro.com: {e}")
            prompt_user("Hãy giải Captcha/nhập OTP (nếu có), hoàn tất đăng ký thuephongtro.com rồi quay lại terminal.")

            # --- Trang 3: chothuenha.com.vn ---
            print("\n-------------------------------------------")
            print("3. Đang mở trang đăng ký: chothuenha.com.vn")
            try:
                page = browser.new_page()
                page.goto("https://chothuenha.com.vn/dang-ky", timeout=30000)
                page.wait_for_load_state("networkidle")
                
                # Tự động điền
                try:
                    page.locator("input[name*='FullName']").first.fill(fullname)
                except:
                    try: page.locator("input[placeholder*='tên']").first.fill(fullname)
                    except: pass
                
                try:
                    page.locator("input[name*='Phone']").first.fill(phone)
                except:
                    try: page.locator("input[placeholder*='thoại']").first.fill(phone)
                    except: pass

                try:
                    page.locator("input[name*='Email']").first.fill(email)
                except:
                    try: page.locator("input[placeholder*='email']").first.fill(email)
                    except: pass
                
                try:
                    page.locator("input[id='Password']").first.fill(password)
                    page.locator("input[id='ConfirmPassword']").first.fill(password)
                except:
                    pass
                
                print("✅ Đã điền thông tin đăng ký chothuenha.com.vn.")
            except Exception as e:
                print(f"⚠️ Lỗi khi mở/điền chothuenha.com.vn: {e}")
            prompt_user("Hãy giải Captcha/nhập OTP (nếu có), hoàn tất đăng ký chothuenha.com.vn rồi quay lại terminal.")

            # --- Trang 4: nhachothue.vn ---
            print("\n-------------------------------------------")
            print("4. Đang mở trang đăng ký: nhachothue.vn")
            try:
                page = browser.new_page()
                url = "https://nhachothue.vn/dang-ky.html"
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle")
                
                # Tự động điền
                try:
                    page.locator("input[name*='name']").first.fill(fullname)
                except:
                    try: page.locator("input[placeholder*='tên']").first.fill(fullname)
                    except: pass
                
                try:
                    page.locator("input[name*='phone']").first.fill(phone)
                except:
                    try: page.locator("input[placeholder*='thoại']").first.fill(phone)
                    except: pass

                try:
                    page.locator("input[name*='email']").first.fill(email)
                except:
                    try: page.locator("input[placeholder*='email']").first.fill(email)
                    except: pass
                
                try:
                    page.locator("input[name*='username']").first.fill(username)
                except:
                    pass

                try:
                    page.locator("input[type='password']").first.fill(password)
                    page.locator("input[name*='re_password']").first.fill(password)
                except:
                    pass
                
                print("✅ Đã điền thông tin đăng ký nhachothue.vn.")
            except Exception as e:
                print(f"⚠️ Lỗi khi mở/điền nhachothue.vn: {e}")
            prompt_user("Hãy giải Captcha/nhập OTP (nếu có), hoàn tất đăng ký nhachothue.vn rồi quay lại terminal.")

            browser.close()
            print("\n🎉 Hoàn thành quá trình đăng ký tài khoản! Cửa sổ trình duyệt đã đóng và Session đã được lưu.")
        except Exception as e:
            print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
