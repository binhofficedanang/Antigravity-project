import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_automation import WebAutomation

def main():
    # Run in headless mode to test full automation
    bot = WebAutomation(headless=True)
    bot.start()
    
    username = "binhofficedanang"
    password = "Binh1995@"
    
    mock_item = {
        "title": "Cho thuê văn phòng 35m2 cực đẹp quận Hải Châu Đà Nẵng",
        "content": "Cần cho thuê văn phòng diện tích 35m2 tại trung tâm quận Hải Châu, Đà Nẵng. Không gian rộng rãi, thoáng mát, đầy đủ tiện ích và ánh sáng tự nhiên tốt, thích hợp làm văn phòng đại diện hoặc công ty khởi nghiệp.",
        "category": "Văn phòng",
        "address": "đường 2/9, P. Hòa Cường Bắc, Hải Châu, Đà Nẵng",
        "district": "Hải Châu",
        "area": "35",
        "price": "7000", # ~7 triệu (7,000 thousands)
        "contact_name": "Nguyễn Ngọc Thiên Bình",
        "phone": "0935723727"
    }
    
    try:
        # Test 123nhadatviet.com
        login_ok = bot.login_123nhadatviet(username, password)
        if login_ok:
            print("Starting real post test on 123nhadatviet.com...")
            post_ok = bot.post_123nhadatviet(mock_item)
            print(f"123nhadatviet.com post success: {post_ok}")
            
        # Test nhadatviet247.net
        login_ok2 = bot.login_nhadatviet247(username, password)
        if login_ok2:
            print("Starting real post test on nhadatviet247.net...")
            post_ok2 = bot.post_nhadatviet247(mock_item)
            print(f"nhadatviet247.net post success: {post_ok2}")
        
    except Exception as e:
        print("Error during post test:", e)
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
