#!/usr/bin/env python3
import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

def main():
    print("Checking 'Cần mua dịch vụ' tab on dashboard...")
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

        # Click the "Cần mua dịch vụ" tab
        print("Clicking 'Cần mua dịch vụ' tab...")
        try:
            bot.page.locator("text=Cần mua dịch vụ").first.click(timeout=5000)
            print("Click successful")
        except Exception as e:
            print(f"Standard click failed: {e}. Trying JS click...")
            bot.page.evaluate("""() => {
                const tabs = Array.from(document.querySelectorAll('div, span, li, a, button'));
                const tab = tabs.find(el => el.innerText && el.innerText.includes('Cần mua dịch vụ'));
                if (tab) tab.click();
            }""")
        time.sleep(5)

        # Capture screenshot
        ss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "muaban_dashboard_service.png")
        bot.safe_screenshot(ss_path)
        print(f"Saved dashboard screenshot to {ss_path}")

        # Extract listings and statuses
        listings = bot.page.evaluate("""() => {
            const results = [];
            const cards = Array.from(document.querySelectorAll('[class*="card"], [class*="item"], tr, li'));
            cards.forEach(card => {
                const titleEl = card.querySelector('h3, h4, h5, [class*="title"]');
                const statusEl = card.querySelector('[class*="status"], [class*="state"]');
                if (titleEl && titleEl.innerText.trim()) {
                    results.push({
                        title: titleEl.innerText.trim(),
                        status: statusEl ? statusEl.innerText.trim() : "Unknown"
                    });
                }
            });
            return results;
        }""")
        
        print("\n=== Listings found under 'Cần mua dịch vụ' ===")
        for idx, item in enumerate(listings[:20]):
            print(f"{idx+1}. Title: {item['title']} | Status: {item['status']}")
        print("==============================================\n")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
