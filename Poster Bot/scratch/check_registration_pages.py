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
        time.sleep(2)
        reg_links = bot.page.locator("a:has-text('Đăng ký'), a:has-text('Đăng Ký'), a[href*='register'], a[href*='dangky'], a[href*='dang-ky']")
        print(f"DiaOcAnPhu register links: {reg_links.count()}")
        for i in range(reg_links.count()):
            print(f"  Link {i}: text='{reg_links.nth(i).text_content().strip()}', href='{reg_links.nth(i).get_attribute('href')}'")
        
        # Go to register page
        if reg_links.count() > 0:
            reg_url = reg_links.first.get_attribute('href')
            if not reg_url.startswith("http"):
                reg_url = "http://diaocanphu.com/" + reg_url
            print(f"Navigating to DiaOcAnPhu register page: {reg_url}")
            bot.page.goto(reg_url, wait_until="domcontentloaded")
            time.sleep(3)
            bot.safe_screenshot("diaocanphu_register_page.png")
            # Find inputs
            inputs = bot.page.locator("input")
            print(f"Inputs count: {inputs.count()}")
            for idx in range(inputs.count()):
                inp = inputs.nth(idx)
                print(f"  Input {idx}: id='{inp.get_attribute('id')}', name='{inp.get_attribute('name')}', type='{inp.get_attribute('type')}'")
    except Exception as e:
        print(f"Error checking DiaOcAnPhu: {e}")
        
    # 2. DatViet24h
    print("\n--- DatViet24h ---")
    try:
        bot.page.goto("https://datviet24h.com.vn/dang-ky.html", wait_until="domcontentloaded", timeout=12000)
        time.sleep(2)
        inputs = bot.page.locator("input")
        print(f"Inputs count: {inputs.count()}")
        for idx in range(inputs.count()):
            inp = inputs.nth(idx)
            print(f"  Input {idx}: id='{inp.get_attribute('id')}', name='{inp.get_attribute('name')}', type='{inp.get_attribute('type')}'")
    except Exception as e:
        print(f"Error checking DatViet24h: {e}")

finally:
    bot.stop()
