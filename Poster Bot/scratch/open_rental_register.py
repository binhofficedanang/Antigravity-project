#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from playwright.sync_api import sync_playwright

def main():
    print("🚀 Khởi động trình duyệt Google Chrome với Session thực của Bot...")
    print("💡 Hãy thực hiện đăng ký và đăng nhập tài khoản mới trên 4 trang:")
    print("  1. phongtro123.com")
    print("  2. thuephongtro.com")
    print("  3. chothuenha.com.vn")
    print("  4. nhachothue.vn")
    print("💡 Sau khi đăng ký/đăng nhập xong, hãy ĐÓNG hoàn toàn trình duyệt để lưu session.")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    session_dir = os.path.join(base_dir, "browser_sessions")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=session_dir,
                headless=False,
                channel="chrome" if os.path.exists("/Applications/Google Chrome.app") else None,
                args=["--start-maximized"]
            )
            
            # Tab 1: phongtro123.com
            page1 = browser.pages[0] if browser.pages else browser.new_page()
            try:
                page1.goto("https://phongtro123.com/dang-ky", timeout=30000)
            except Exception as e:
                print(f"Error opening phongtro123: {e}")
            
            # Tab 2: thuephongtro.com
            try:
                page2 = browser.new_page()
                page2.goto("https://thuephongtro.com/dang-ky", timeout=30000)
            except Exception as e:
                print(f"Error opening thuephongtro: {e}")
            
            # Tab 3: chothuenha.com.vn
            try:
                page3 = browser.new_page()
                page3.goto("https://chothuenha.com.vn/dang-ky", timeout=30000)
            except Exception as e:
                print(f"Error opening chothuenha.com.vn: {e}")
            
            # Tab 4: nhachothue.vn
            try:
                page4 = browser.new_page()
                page4.goto("https://nhachothue.vn/dang-ky.html", timeout=30000)
            except Exception as e:
                try:
                    page4.goto("https://nhachothue.vn/dang-ky", timeout=30000)
                except Exception as e2:
                    try:
                        page4.goto("https://nhachothue.vn/", timeout=30000)
                    except Exception as e3:
                        print(f"Error opening nhachothue: {e3}")
            
            # Chờ người dùng đóng trình duyệt
            while True:
                try:
                    # Kiểm tra xem tab 1 còn hoạt động không
                    _ = page1.url
                    time.sleep(1)
                except Exception:
                    break
                    
            browser.close()
            print("🔒 Trình duyệt đã đóng. Session đã được lưu thành công!")
        except Exception as e:
            print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
