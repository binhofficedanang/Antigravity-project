#!/usr/bin/env python3
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_automation import WebAutomation

def main():
    print("Dumping draft modal page...")
    bot = WebAutomation(headless=False)
    try:
        bot.start()
        
        # 1. Login (using persistent session)
        username = "0935723727"
        password = "Binh1995@"
        login_ok = bot.login_muaban(username, password)
        if not login_ok:
            print("❌ Login failed.")
            return

        # 2. Go to posting page
        print("- Navigating to posting page...")
        bot.page.goto("https://muaban.net/dang-tin", wait_until="domcontentloaded", timeout=60000)
        bot._wait_for_cloudflare(bot.page, timeout_secs=15)
        time.sleep(5)

        # 3. Save screenshot and HTML of modal state
        print("- Capturing draft modal...")
        bot.safe_screenshot(os.path.join(os.path.dirname(os.path.abspath(__file__)), "muaban_draft_modal.png"))
        
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "muaban_draft_modal.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(bot.page.content())
        print(f"  ✅ Saved HTML to {html_path}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
