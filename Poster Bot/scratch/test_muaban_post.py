#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
from web_automation import WebAutomation

def main():
    print("Testing muaban.net login and post...")
    
    with open('config.json', 'r') as f:
        config = json.load(f)
        
    acc = config.get("muaban.net", {})
    username = acc.get("username")
    password = acc.get("password")
    
    if not username or not password:
        print("Missing credentials in config.json")
        return
        
    bot = WebAutomation(headless=False)
    try:
        bot.start()
        
        login_ok = bot.login_muaban(username, password)
        if login_ok:
            test_item = {
                "title": "Cho thuê tòa nhà văn phòng đường 2/9 diện tích 1000m2",
                "area": "1000 m2",
                "price": "500 triệu/tháng",
                "address": "Đường 2/9, Hải Châu, Đà Nẵng",
                "content": "Tòa nhà đẹp, nội thất đầy đủ.\\nLiên hệ ngay.",
                "source_url": "https://officedanang.vn/property/toa-nha-van-phong-duong-2-9-1000m2/"
            }
            post_result = bot.post_muaban(test_item)
            print(f"\n============================================================\n✅ KẾT QUẢ ĐĂNG TIN: {'THÀNH CÔNG' if post_result else 'THẤT BẠI'}\n============================================================\n")
        else:
            print("Login failed.")
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        bot.stop()
        
if __name__ == "__main__":
    main()
