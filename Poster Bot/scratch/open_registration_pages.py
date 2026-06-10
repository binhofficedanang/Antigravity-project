#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from playwright.sync_api import sync_playwright

def main():
    print("🚀 Khởi động trình duyệt Google Chrome với Session thực của Bot...")
    print("💡 Hãy thực hiện đăng ký tài khoản mới trên 2 trang:")
    print("  1. raovatdanang.vn")
    print("  2. chodanang.com")
    print("💡 Sau khi đăng ký và đăng nhập xong, hãy ĐÓNG trình duyệt để lưu lại cookie/session.")
    
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
            
            # Tab 1: raovatdanang.vn
            page1 = browser.pages[0] if browser.pages else browser.new_page()
            try:
                page1.goto("https://raovatdanang.vn/wp-login.php?action=register", timeout=20000)
            except Exception:
                page1.goto("https://raovatdanang.vn/", timeout=20000)
                
            # Tab 2: chodanang.com
            page2 = browser.new_page()
            page2.goto("http://chodanang.com/", timeout=20000)
            
            # Chờ người dùng đóng trình duyệt
            while True:
                try:
                    # Kiểm tra xem các tab có còn hoạt động không
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
