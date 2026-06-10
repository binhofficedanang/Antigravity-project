#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from playwright.sync_api import sync_playwright

def main():
    print("🚀 Khởi động trình duyệt Google Chrome với Session thực của Bot...")
    print("💡 Trình duyệt sẽ mở ra. Bạn có thể tự do truy cập bất kỳ trang web nào (như datviet24h.com.vn, raovat247.net, nhadat24h.net), tiến hành đăng nhập và giải captcha.")
    print("💡 Sau khi đăng nhập xong, hãy ĐÓNG cửa sổ trình duyệt Chrome lại để lưu Session.")
    
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
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto("https://google.com")
            
            # Chờ cho đến khi người dùng đóng trình duyệt
            while True:
                try:
                    # Kiểm tra xem page có còn hoạt động không
                    _ = page.url
                    time.sleep(1)
                except Exception:
                    break
                    
            browser.close()
            print("🔒 Trình duyệt đã được đóng. Session đã được lưu thành công!")
        except Exception as e:
            print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
