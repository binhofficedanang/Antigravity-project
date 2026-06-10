import sys
import os
import time
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_automation import WebAutomation

def main():
    bot = WebAutomation(headless=True)
    bot.start()
    
    username = "binhofficedanang"
    password = "Binh1995@"
    
    mock_item = {
        "title": "Cho thuê văn phòng 35m2 cực đẹp quận Hải Châu Đà Nẵng",
        "content": "Cần cho thuê văn phòng diện tích 35m2 tại trung tâm quận Hải Châu, Đà Nẵng. Không gian rộng rãi, thoáng mát, đầy đủ tiện ích và ánh sáng tự nhiên tốt, thích hợp làm văn phòng đại diện hoặc công ty khởi nghiệp.",
        "category": "Văn phòng",
        "address": "đường 2/9, Hải Châu, Đà Nẵng",
        "district": "Hải Châu",
        "area": "35",
        "price": "7000",
        "contact_name": "Nguyễn Ngọc Thiên Bình",
        "phone": "0935723727"
    }
    
    # Register dialog event listener to capture alert messages
    def handle_dialog(dialog):
        print(f"🚨 Dialog popped up: {dialog.type} - Message: '{dialog.message}'")
        dialog.dismiss()
        
    bot.page.on("dialog", handle_dialog)
    
    try:
        # Login
        bot.login_123nhadatviet(username, password)
        
        # Navigate to dang-tin
        bot.page.goto("http://123nhadatviet.com/dang-tin.html", wait_until="domcontentloaded")
        time.sleep(2)
        
        # Fill
        bot.page.fill("#tieude", mock_item["title"])
        bot.page.fill("#noidung", mock_item["content"])
        bot.page.select_option("#loaitin", "2") # Cho thuê
        bot.page.select_option("#loaibds", "6") # Văn phòng
        bot.page.select_option("#tinh", "3") # Đà Nẵng
        time.sleep(1.5)
        
        # Select district
        bot.page.select_option("#huyen", "584") # Hải Châu
        time.sleep(1.5)
        
        # Fill address, area, price
        bot.page.fill("#diachi", mock_item["address"])
        bot.page.fill("#dientich", mock_item["area"])
        bot.page.fill("#gia", mock_item["price"])
        bot.page.select_option("#cachtinh", "1")
        
        bot.page.fill("#lienhe", mock_item["contact_name"])
        bot.page.fill("#dienthoai", mock_item["phone"])
        
        # Solve captcha
        captcha_code = bot.solve_image_captcha_free(bot.page, "img.captchagenerator")
        print(f"Solved Captcha: {captcha_code}")
        if captcha_code:
            bot.page.fill("#captcha", captcha_code)
            
        # Click submit and wait for dialog/alert
        print("Clicking submit button...")
        submit_btn = bot.page.locator("input[type='submit'], button:has-text('Đăng tin'), input[value='Đăng tin'], a:has-text('Đăng tin')").first
        submit_btn.click()
        
        time.sleep(5)
        print(f"Final Page URL: {bot.page.url}")
        
    except Exception as e:
        print("Error:", e)
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
