import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

bot = WebAutomation(headless=False)
try:
    bot.start()
    print("Navigating to https://maumau.vn/ ...")
    bot.page.goto("https://maumau.vn/", wait_until="domcontentloaded", timeout=15000)
    time.sleep(3)
    bot.safe_screenshot("maumau_homepage.png")
    print(f"Current URL: {bot.page.url}")
    
    # Check for login links
    login_btn = bot.page.locator("a:has-text('Đăng nhập'), a:has-text('Log in'), a[href*='login']")
    print(f"Login buttons found: {login_btn.count()}")
    if login_btn.count() > 0:
        for i in range(login_btn.count()):
            print(f"Btn {i}: text='{login_btn.nth(i).text_content().strip()}', href='{login_btn.nth(i).get_attribute('href')}'")
finally:
    bot.stop()
