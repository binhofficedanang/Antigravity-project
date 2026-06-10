#!/usr/bin/env python3
"""
Test script: Kiểm tra login muaban.net với logic mới
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_automation import WebAutomation

def test_login():
    print("=" * 60)
    print("TEST: Đăng nhập muaban.net")
    print("=" * 60)

    bot = WebAutomation(headless=False)
    try:
        bot.start()
        print("✅ Browser đã khởi động\n")

        username = "0935723727"
        password = "Binh1995@"

        result = bot.login_muaban(username, password)

        print()
        print("=" * 60)
        if result:
            print("✅ KẾT QUẢ: ĐĂNG NHẬP THÀNH CÔNG")
        else:
            print("❌ KẾT QUẢ: ĐĂNG NHẬP THẤT BẠI")
        print("=" * 60)

        # Kiểm tra URL hiện tại
        print(f"\nURL hiện tại: {bot.page.url}")
        print(f"Title: {bot.page.title()}")

        # Hiển thị cookies
        cookies = bot.context.cookies()
        print(f"\nTổng số cookies: {len(cookies)}")
        for c in cookies[:10]:
            print(f"  - {c['name']} = {c['value'][:30]}...")

    finally:
        bot.stop()

if __name__ == "__main__":
    test_login()
