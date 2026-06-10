import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

bot = WebAutomation(headless=False)
try:
    bot.start()
    print("Navigating to registration page of datviet24h.com.vn...")
    bot.page.goto("https://datviet24h.com.vn/dang-ky.html", wait_until="domcontentloaded", timeout=15000)
    time.sleep(3)
    bot.safe_screenshot("datviet24h_register_loaded.png")
    
    # Check elements on register page
    print(f"Content: {bot.page.url}")
    username_input = bot.page.locator("input#username, input[name='username'], input#txtTenDangNhap")
    print(f"Username inputs found: {username_input.count()}")
    
finally:
    bot.stop()
