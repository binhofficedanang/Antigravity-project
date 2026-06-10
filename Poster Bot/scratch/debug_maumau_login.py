import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

bot = WebAutomation(headless=False)
try:
    bot.start()
    print("Navigating directly to maumau login page...")
    bot.page.goto("https://id.maumau.vn/login?return-url=https%3A%2F%2Fmaumau.vn&code=maumau", wait_until="domcontentloaded", timeout=15000)
    time.sleep(3)
    bot.safe_screenshot("maumau_login_page_loaded.png")
    print(f"Current URL: {bot.page.url}")
    
    # Fill login form
    bot.page.fill("input#email", "binh.officedanang@gmail.com")
    bot.page.fill("input#password", "Binh1995@")
    bot.safe_screenshot("maumau_login_filled.png")
    
    # Click submit
    print("Clicking submit...")
    bot.page.click("button[type='submit']")
    time.sleep(6)
    
    bot.safe_screenshot("maumau_after_login_click.png")
    print(f"Final URL: {bot.page.url}")
finally:
    bot.stop()
