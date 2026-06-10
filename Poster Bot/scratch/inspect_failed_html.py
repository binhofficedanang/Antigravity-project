import sys
import os
import time

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
    
    try:
        # Login
        bot.login_123nhadatviet(username, password)
        
        # Go to posting page
        bot.page.goto("http://123nhadatviet.com/dang-tin.html", wait_until="domcontentloaded")
        time.sleep(2)
        
        # Fill fields
        bot.page.fill("#tieude", mock_item["title"])
        bot.page.fill("#noidung", mock_item["content"])
        bot.page.select_option("#loaitin", "2") # Cho thuê
        bot.page.select_option("#loaibds", "6") # Văn phòng
        bot.page.select_option("#tinh", "3") # Đà Nẵng
        time.sleep(1.5)
        bot.page.select_option("#huyen", "584") # Hải Châu
        time.sleep(1.5)
        
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
            
        # Submit
        print("Submitting...")
        submit_btn = bot.page.locator("input[type='submit'], button:has-text('Đăng tin'), input[value='Đăng tin'], a:has-text('Đăng tin')").first
        submit_btn.click()
        
        time.sleep(5)
        
        # Save HTML
        html = bot.page.content()
        with open("failed_submit_source.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Failed page source saved to failed_submit_source.html")
        
        # Check if there are any error class elements
        errors = bot.page.evaluate("""() => {
            // Find all divs or spans containing error text or with red color styles
            return Array.from(document.querySelectorAll('.error, .require, [style*="red"], [style*="Red"]'))
                .map(el => ({ tag: el.tagName, text: el.innerText.strip(), visible: el.offsetWidth > 0 }))
                .filter(item => item.text.length > 0 && item.visible);
        }""")
        print("Active error elements on the reloaded page:")
        for err in errors:
            print(f"  - [{err['tag']}] {err['text']}")
            
    except Exception as e:
        print("Error:", e)
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
