#!/usr/bin/env python3
import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

def main():
    print("Inspecting dashboard listings...")
    bot = WebAutomation(headless=True)
    try:
        bot.start()
        
        # Read config
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        muaban_config = config.get("muaban.net", {})
        
        username = muaban_config.get("username", "")
        password = muaban_config.get("password", "")
        
        # We can bypass login check if session is already active
        print("Logging in...")
        bot.page.goto("https://muaban.net/", wait_until="domcontentloaded", timeout=60000)
        bot._wait_for_cloudflare(bot.page, timeout_secs=10)
        time.sleep(3)
        
        if "/account/login" in bot.page.url or bot.page.locator("a:has-text('Đăng nhập')").count() > 0:
            print("Not logged in, performing login...")
            login_ok = bot.login_muaban(username, password)
            if not login_ok:
                print("❌ Login failed.")
                return
        else:
            print("✅ Already logged in from session!")

        # Go to dashboard
        dashboard_url = "https://muaban.net/dashboard/manage-listing"
        print(f"Navigating to dashboard: {dashboard_url}...")
        bot.page.goto(dashboard_url, wait_until="domcontentloaded", timeout=60000)
        bot._wait_for_cloudflare(bot.page, timeout_secs=10)
        time.sleep(5)

        # Click the 'Tất cả' tab
        print("Clicking 'Tất cả' tab...")
        try:
            bot.page.locator("text=Tất cả").first.click(timeout=5000)
            print("Standard locator click worked!")
        except Exception as e:
            print(f"Standard locator click failed: {e}. Trying text selector click...")
            bot.page.click("text=Tất cả", timeout=5000)
            
        time.sleep(5)
        bot.safe_screenshot("scratch/muaban_dashboard_all_clicked.png")

        # Get all text content of listing containers
        print("Extracting elements below tabs...")
        page_elements = bot.page.evaluate("""() => {
            // Find all h3/h4/h5 elements or texts that could be titles
            const divs = Array.from(document.querySelectorAll('div, a, p, h3, h4'));
            return divs.map(d => {
                if (d.innerText && d.innerText.includes('WINK HOTEL')) {
                    return {
                        tag: d.tagName,
                        className: d.className,
                        text: d.innerText.substring(0, 100)
                    };
                }
                return null;
            }).filter(Boolean);
        }""")

        print("\n--- Matching elements containing WINK HOTEL ---")
        for el in page_elements:
            print(f"Tag: {el['tag']} | Class: {el['className']} | Text: {el['text']}")
        print("------------------------------------------------\n")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
