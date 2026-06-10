import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

bot = WebAutomation(headless=False)
try:
    bot.start()
    
    # Try different URLs
    urls = [
        "http://diaocanphu.com/dang-nhap.html",
        "http://diaocanphu.com/dangnhap.html",
        "http://diaocanphu.com/thanh-vien/dang-nhap.html",
    ]
    for url in urls:
        print(f"Testing URL: {url}")
        try:
            bot.page.goto(url, wait_until="domcontentloaded", timeout=8000)
            time.sleep(2)
            print(f"Successfully loaded. Current URL: {bot.page.url}")
            inputs = bot.page.locator("input[type='text'], input[type='password']").count()
            print(f"Text/Password Inputs found: {inputs}")
            if inputs > 0:
                bot.safe_screenshot(f"diaocanphu_{url.replace('/', '_').replace(':', '')}.png")
                break
        except Exception as e:
            print(f"Failed to load: {e}")
            
finally:
    bot.stop()
