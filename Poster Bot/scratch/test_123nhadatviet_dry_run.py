import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_automation import WebAutomation

def main():
    # Run in headful/headless mode
    bot = WebAutomation(headless=True)
    bot.start()
    
    # Mock listing item
    mock_item = {
        "title": "Bán căn hộ chung cư 2 phòng ngủ giá rẻ cực đẹp tại Đà Nẵng",
        "description": "Căn hộ thiết kế hiện đại, đầy đủ tiện nghi, vị trí đắc địa giao thông thuận tiện. Phù hợp cho hộ gia đình định cư lâu dài hoặc đầu tư cho thuê.",
        "type": "Bán",
        "property_type": "Chung cư",
        "city": "Đà Nẵng",
        "district": "Hải Châu",
        "address": "123 Đường Nguyễn Văn Linh",
        "area": "75",
        "price": "2.5 tỷ",
        "contact_name": "Nguyễn Văn A",
        "phone": "0905123456"
    }
    
    try:
        # We will manually perform the post steps without clicking the final submit
        print("Testing form fill logic on 123nhadatviet.com...")
        
        # Open page
        bot.page.goto("http://123nhadatviet.com/dang-tin.html", wait_until="domcontentloaded")
        bot._wait_for_cloudflare(bot.page, timeout_secs=15)
        time.sleep(2)
        
        # Fill Title
        bot.page.fill("#tieude", mock_item["title"])
        
        # Fill Content
        bot.page.fill("#noidung", mock_item["description"])
        
        # Select Category
        bot.page.select_option("#loaitin", "1") # Cần bán
        
        # Select Property Type
        bot.page.select_option("#loaibds", "4") # Chung cư
        
        # Select City
        bot.page.select_option("#tinh", "3") # Đà Nẵng
        time.sleep(1.5)
        
        # Select District
        bot.page.select_option("#huyen", "25") # Hải Châu (option ID 25 or similar)
        
        # Fill Address
        bot.page.fill("#diachi", mock_item["address"])
        
        # Fill Area
        bot.page.fill("#dientich", mock_item["area"])
        
        # Fill Price (2.5 tỷ -> 2,500,000 thousands)
        bot.page.fill("#gia", "2500000")
        bot.page.select_option("#cachtinh", "1")
        
        # Contact
        bot.page.fill("#lienhe", mock_item["contact_name"])
        bot.page.fill("#dienthoai", mock_item["phone"])
        
        # Test Captcha Solving
        print("Testing captcha solving...")
        captcha_code = bot.solve_image_captcha(bot.page, "img.captchagenerator")
        print(f"Solved Captcha Code: '{captcha_code}'")
        if captcha_code:
            bot.page.fill("#captcha", captcha_code)
            
        # Take a screenshot of the filled form
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bot.safe_screenshot(os.path.join(script_dir, "test_123nhadatviet_dry_run.png"))
        print("Dry run screenshot saved to test_123nhadatviet_dry_run.png successfully!")
        
    except Exception as e:
        print("Error during test:", e)
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
