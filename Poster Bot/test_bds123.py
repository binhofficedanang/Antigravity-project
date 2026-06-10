import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from web_automation import WebAutomation

USERNAME = "0935723727"
PASSWORD = "Binh1995@"

test_item = {
    "title": "[TEST] Văn phòng cho thuê tại Cloud 9 - Đà Nẵng",
    "description": "Tòa nhà Cloud 9 tọa lạc tại trung tâm thành phố Đà Nẵng. Diện tích đa dạng từ 30m² đến 300m². Có đầy đủ tiện nghi, thang máy, bãi đỗ xe. Liên hệ để được tư vấn.",
    "content": "Tòa nhà Cloud 9 tọa lạc tại trung tâm thành phố Đà Nẵng. Diện tích đa dạng từ 30m² đến 300m². Có đầy đủ tiện nghi, thang máy, bãi đỗ xe. Liên hệ để được tư vấn.",
    "address": "Đà Nẵng",
    "price": "15000000",
    "area": "50",
    "phone": "0935723727",
    "contact_name": "Binh Office Da Nang",
    "source_url": "https://officedanang.vn/property/toa-nha-cloud-9-van-phong-cho-thue/"
}

bot = None
try:
    print("Starting WebAutomation (headless=True) for bds123.vn test...", flush=True)
    bot = WebAutomation(headless=True)
    bot.start()
    
    print("Testing login_bds123...", flush=True)
    login_ok = bot.login_bds123(USERNAME, PASSWORD)
    if login_ok:
        print("✅ Login bds123.vn succeeded!", flush=True)
        print("Testing post_bds123...", flush=True)
        post_ok = bot.post_bds123(test_item)
        print(f"✅ Post result: {post_ok}", flush=True)
    else:
        print("❌ Login bds123.vn failed!", flush=True)
except Exception as e:
    print(f"❌ Error during test: {e}", flush=True)
    import traceback; traceback.print_exc()
finally:
    if bot:
        bot.stop()
        print("🔒 Browser closed.", flush=True)
