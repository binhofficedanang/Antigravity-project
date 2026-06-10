#!/usr/bin/env python3
"""
End-to-end test of post_muaban using actual CSV data.
Does NOT submit - stops just before clicking submit.
"""
import sys, os, time, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

def main():
    # Read first item from data.csv
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data.csv")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        item = next(reader)

    print("=== Test item ===")
    print(f"  Title: {item.get('title', '')[:60]}")
    print(f"  District: {item.get('district', '')}")
    print(f"  Area: {item.get('area', '')}")
    print(f"  Price: {item.get('price', '')[:30]}")
    print(f"  Address: {item.get('address', '')[:40]}")
    print(f"  Ward: '{item.get('ward', '')}'")
    print()

    # Read config for muaban.net
    import json
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    muaban_config = config.get("muaban.net", {})

    bot = WebAutomation(headless=False)
    try:
        bot.start()
        # Login
        username = muaban_config.get("username", "")
        password = muaban_config.get("password", "")
        print(f"Logging in to muaban.net with {username}...")
        login_ok = bot.login_muaban(username, password)
        if not login_ok:
            print("❌ Đăng nhập muaban.net thất bại.")
            return

        # Use post_muaban directly in dry-run mode
        result = bot.post_muaban(item, dry_run=True)
        print(f"\n=== Kết quả (Dry Run): {'✅ Thành công' if result else '❌ Thất bại'} ===")
    except Exception as e:
        print(f"❌ Exception: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
