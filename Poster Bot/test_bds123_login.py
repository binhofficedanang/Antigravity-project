import os
import sys
import time
sys.path.insert(0, "Poster Bot")
from web_automation import WebAutomation

USERNAME = "0935723727"
PASSWORD = "Binh1995@"

bot = None
try:
    print("Starting WebAutomation (headless=True) to test bds123 login...", flush=True)
    bot = WebAutomation(headless=True)
    bot.start()
    
    # Force go to login page directly
    print("Navigating to login page...", flush=True)
    bot.page.goto("https://bds123.vn/dang-nhap.html", wait_until="domcontentloaded")
    time.sleep(2)
    bot.safe_screenshot("bds123_test_login_page_loaded.png")
    
    print("Filling credentials...", flush=True)
    bot.page.fill("input[name='loginname']", USERNAME)
    time.sleep(0.5)
    bot.page.fill("input[name='password']", PASSWORD)
    time.sleep(0.5)
    
    bot.safe_screenshot("bds123_test_login_filled.png")
    
    print("Clicking login...", flush=True)
    bot.page.click("button:has-text('Đăng nhập')")
    time.sleep(5)
    
    bot.safe_screenshot("bds123_test_login_result.png")
    print(f"Current URL: {bot.page.url}", flush=True)
    
    # Check if header dropdown has user's name
    user_ctrl = bot.page.locator(".js-header-control-user-login")
    if user_ctrl.count() > 0:
        print(f"Header control HTML: {user_ctrl.first.inner_html()}", flush=True)
        print(f"Header control Text: {user_ctrl.first.inner_text().strip()}", flush=True)
        
except Exception as e:
    print(f"❌ Error: {e}", flush=True)
finally:
    if bot:
        bot.stop()
        print("🔒 Browser closed.", flush=True)
