#!/usr/bin/env python3
"""
Script thiết lập session muaban.net lần đầu tiên.
Chạy script này MỘT LẦN để lưu cookies/session vào disk.
Sau đó bot sẽ tự động dùng session đã lưu mà không cần xác minh Cloudflare nữa.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
from web_automation import WebAutomation

def main():
    print("=" * 60)
    print("  THIẾT LẬP SESSION MUABAN.NET (Chạy 1 lần)")
    print("=" * 60)
    print()
    print("Sắp mở trình duyệt Chrome. Bạn cần:")
    print("  1. Chờ Cloudflare xác minh tự động (thường dưới 10 giây)")
    print("  2. Đăng nhập vào muaban.net nếu chưa đăng nhập")
    print("  3. Sau khi vào được trang chủ, script sẽ lưu session tự động")
    print()
    import sys
    if sys.stdin.isatty():
        input("Nhấn ENTER để bắt đầu...")
    else:
        print("Chạy ở chế độ không tương tác, bỏ qua nhấn ENTER...")

    # Đọc config
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)

    account = config.get('muaban.net', {})
    username = account.get('phone', account.get('email', ''))
    password = account.get('password', '')

    print(f"\nTài khoản: {username}")
    print(f"Session sẽ lưu tại: browser_sessions/\n")

    bot = WebAutomation(headless=False)
    bot.start()

    try:
        print(">> Đang mở muaban.net...")
        bot.page.goto("https://muaban.net/", wait_until="domcontentloaded", timeout=60000)

        print(">> Chờ Cloudflare...")
        ok = bot._wait_for_cloudflare(bot.page, timeout_secs=60)

        if ok:
            print("✅ Cloudflare đã vượt qua!")
        else:
            print("⚠️ Timeout - tiếp tục thử đăng nhập...")

        # Kiểm tra đã đăng nhập chưa
        time.sleep(2)
        already_logged = bot.page.locator("[class*='avatar'], [class*='user-name'], a[href*='/ca-nhan']").count() > 0
        if already_logged:
            print("✅ Đã đăng nhập sẵn!")
        else:
            print(">> Thực hiện đăng nhập...")
            bot.login_muaban(username, password)

        # Kiểm tra vào trang đăng tin
        print("\n>> Kiểm tra trang đăng tin...")
        bot.page.goto("https://muaban.net/dang-tin", wait_until="domcontentloaded", timeout=30000)
        bot._wait_for_cloudflare(bot.page, timeout_secs=30)

        title = bot.page.title()
        url = bot.page.url
        print(f"  Title: {title}")
        print(f"  URL: {url}")

        if 'Chờ' in title or 'moment' in title:
            print("\n⚠️ Vẫn còn Cloudflare. Hãy giải thủ công trong trình duyệt...")
            print("Chờ bạn xác minh... (tối đa 60 giây)")
            bot._wait_for_cloudflare(bot.page, timeout_secs=60)

        print("\n✅ Session đã lưu thành công!")
        print("   Bot sẽ dùng session này cho các lần chạy tiếp theo.")
        print("\nGiữ trình duyệt mở 5 giây rồi đóng...")
        time.sleep(5)

    finally:
        bot.stop()
        print("\n🎉 Xong! Giờ bạn có thể chạy bot đăng tin bình thường.")

if __name__ == "__main__":
    main()
