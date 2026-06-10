#!/usr/bin/env python3
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_automation import WebAutomation

def main():
    print("Testing address selection on Muaban.net...")
    bot = WebAutomation(headless=False)
    try:
        bot.start()
        
        # 1. Login
        username = "0935723727"
        password = "Binh1995@"
        login_ok = bot.login_muaban(username, password)
        if not login_ok:
            print("❌ Login failed.")
            return

        # 2. Go to posting page
        bot.page.goto("https://muaban.net/dang-tin", wait_until="domcontentloaded", timeout=60000)
        bot._wait_for_cloudflare(bot.page, timeout_secs=15)
        time.sleep(3)

        # 3. Handle draft modal
        try:
            if bot.page.locator("button:has-text('Đăng tin mới')").count() > 0:
                bot.page.click("button:has-text('Đăng tin mới')", timeout=3000)
                time.sleep(2)
        except: pass

        # 4. Select category
        bot.page.click("text=Bất động sản", timeout=3000)
        time.sleep(1)
        bot.page.click("text=Cho thuê", timeout=3000)
        time.sleep(1)
        bot.page.click("text=Văn phòng, mặt bằng", timeout=3000)
        time.sleep(3)

        # 5. Click City selection dropdown
        print("- Clicking City dropdown...")
        bot.page.click("#city_id", timeout=5000)
        time.sleep(2)
        
        # Take screenshot of City selection modal
        bot.safe_screenshot(os.path.join(os.path.dirname(os.path.abspath(__file__)), "city_clicked.png"))
        
        # Try to select Đà Nẵng
        print("- Selecting Đà Nẵng...")
        # Let's find any element containing 'Đà Nẵng' in the modal
        danang_locator = bot.page.locator("text=Đà Nẵng, [class*='item']:has-text('Đà Nẵng'), li:has-text('Đà Nẵng')").last
        danang_locator.click(timeout=5000)
        time.sleep(2)
        print("  Selected City!")

        # 6. Click District dropdown
        print("- Clicking District dropdown...")
        bot.page.click("#district_id", timeout=5000)
        time.sleep(2)
        
        # Take screenshot of District selection modal
        bot.safe_screenshot(os.path.join(os.path.dirname(os.path.abspath(__file__)), "district_clicked.png"))
        
        # Try to select 'Hải Châu' or another district
        district_val = "Hải Châu"
        print(f"- Selecting district: {district_val}...")
        district_locator = bot.page.locator(f"text={district_val}, [class*='item']:has-text('{district_val}'), li:has-text('{district_val}')").last
        district_locator.click(timeout=5000)
        time.sleep(2)
        print("  Selected District!")

        # 7. Click Ward dropdown
        print("- Clicking Ward dropdown...")
        bot.page.click("#ward_id", timeout=5000)
        time.sleep(2)
        
        # Take screenshot of Ward selection modal
        bot.safe_screenshot(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ward_clicked.png"))

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
