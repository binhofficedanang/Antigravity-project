import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

bot = WebAutomation(headless=False)
try:
    bot.start()
    
    # 1. DiaOcAnPhu
    print("\n--- DiaOcAnPhu ---")
    try:
        bot.page.goto("http://diaocanphu.com/", wait_until="domcontentloaded", timeout=12000)
        time.sleep(3)
        bot.safe_screenshot("diaocanphu_home.png")
        links = bot.page.locator("a:has-text('Đăng nhập'), a:has-text('Đăng Nhập'), a[href*='login'], a[href*='dangnhap'], a[href*='dang-nhap']")
        print(f"DiaOcAnPhu login links found: {links.count()}")
        for i in range(links.count()):
            print(f"  Link {i}: text='{links.nth(i).text_content().strip()}', href='{links.nth(i).get_attribute('href')}'")
    except Exception as e:
        print(f"Error loading DiaOcAnPhu: {e}")
        
    # 2. DangTinBatDongSan
    print("\n--- DangTinBatDongSan ---")
    try:
        bot.page.goto("https://dangtinbatdongsan.vn/qttv", wait_until="domcontentloaded", timeout=12000)
        time.sleep(3)
        print(f"URL: {bot.page.url}")
        # Let's inspect the submit button selector on the login form
        submit_btn = bot.page.locator("input[type='submit'], button[type='submit'], .btn, input#btnDangNhap, button#btnDangNhap")
        print(f"DangTinBatDongSan submit buttons found: {submit_btn.count()}")
        for i in range(submit_btn.count()):
            print(f"  Btn {i}: id='{submit_btn.nth(i).get_attribute('id')}', class='{submit_btn.nth(i).get_attribute('class')}', value='{submit_btn.nth(i).get_attribute('value')}', tag='{submit_btn.nth(i).evaluate('el => el.tagName')}'")
    except Exception as e:
        print(f"Error loading DangTinBatDongSan: {e}")

finally:
    bot.stop()
