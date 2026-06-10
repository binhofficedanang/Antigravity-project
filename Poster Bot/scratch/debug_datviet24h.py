import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

bot = WebAutomation(headless=False)
try:
    bot.start()
    print("Navigating to https://datviet24h.com.vn/ ...")
    bot.page.goto("https://datviet24h.com.vn/", wait_until="domcontentloaded", timeout=15000)
    time.sleep(3)
    
    # Find and click login button on header
    login_btn = bot.page.locator("a:has-text('Đăng nhập'), a[href*='login'], a[href*='dang-nhap'], a[href*='dangnhap']")
    print(f"Login links found: {login_btn.count()}")
    if login_btn.count() > 0:
        for i in range(login_btn.count()):
            print(f"Btn {i}: text='{login_btn.nth(i).text_content().strip()}', href='{login_btn.nth(i).get_attribute('href')}'")
        
        print("Clicking the first login link...")
        login_btn.first.click()
        time.sleep(4)
        print(f"Current URL after click: {bot.page.url}")
        bot.safe_screenshot("datviet24h_login_page_loaded.png")
finally:
    bot.stop()
