#!/usr/bin/env python3
import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

def main():
    print("Checking all listings on dashboard...")
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
        
        login_ok = bot.login_muaban(username, password)
        if not login_ok:
            print("❌ Login failed.")
            return

        # Navigate to manage listing dashboard
        dashboard_url = "https://muaban.net/dashboard/manage-listing"
        print(f"Navigating to dashboard: {dashboard_url}...")
        bot.page.goto(dashboard_url, wait_until="domcontentloaded", timeout=60000)
        bot._wait_for_cloudflare(bot.page, timeout_secs=10)
        time.sleep(5)

        # Click the "Tất cả" tab
        print("Clicking 'Tất cả' tab...")
        # Let's find the element containing 'Tất cả'
        bot.page.evaluate("""() => {
            const tabs = Array.from(document.querySelectorAll('div, span, li, a, button'));
            const tab = tabs.find(el => el.innerText && el.innerText.includes('Tất cả'));
            if (tab) tab.click();
        }""")
        time.sleep(5)

        # Capture screenshot
        ss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "muaban_dashboard_all.png")
        bot.safe_screenshot(ss_path)
        print(f"Saved dashboard screenshot to {ss_path}")

        # Extract listings and statuses
        listings = bot.page.evaluate("""() => {
            const results = [];
            // Let's find all cards or items below the tab bar
            const elements = Array.from(document.querySelectorAll('*'));
            // Find elements that have text of a listing title and state
            // Let's dump all text for analysis if needed
            return elements.map(el => {
                if (el.tagName === 'H3' || el.tagName === 'H4' || (el.className && el.className.toString().includes('title'))) {
                    return el.innerText.trim();
                }
                return null;
            }).filter(Boolean);
        }""")
        
        print("\n=== Header elements / Titles found ===")
        for idx, t in enumerate(listings[:20]):
            print(f"- {t}")
        print("======================================\n")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
