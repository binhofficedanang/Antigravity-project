#!/usr/bin/env python3
"""
Live posting test for muaban.net.
Submits the listing to the portal and verifies the result.
"""
import sys
import os
import time
import csv
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

def main():
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data.csv")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        item = next(reader)

    print("=== LIVE POSTING ITEM ===")
    print(f"  Title: {item.get('title', '')[:60]}")
    print(f"  District: {item.get('district', '')}")
    print(f"  Area: {item.get('area', '')}")
    print(f"  Price: {item.get('price', '')[:30]}")
    print(f"  Address: {item.get('address', '')[:40]}")
    print()

    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    muaban_config = config.get("muaban.net", {})

    bot = WebAutomation(headless=False)
    try:
        bot.start()
        username = muaban_config.get("username", "")
        password = muaban_config.get("password", "")
        print(f"Logging in to muaban.net with {username}...")
        login_ok = bot.login_muaban(username, password)
        if not login_ok:
            print("❌ Đăng nhập muaban.net thất bại.")
            return

        print("Executing live post (dry_run=False)...")
        result = bot.post_muaban(item, dry_run=False)
        print(f"\n=== Kết quả đăng tin: {'✅ THÀNH CÔNG' if result else '❌ THẤT BẠI'} ===")
    except Exception as e:
        print(f"❌ Exception: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
