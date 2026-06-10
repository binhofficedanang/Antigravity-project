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
    
    # Listen to dialog event
    def handle_dialog(dialog):
        print(f"🚨 Dialog: {dialog.message}")
        dialog.dismiss()
    bot.page.on("dialog", handle_dialog)
    
    try:
        # Login
        bot.login_123nhadatviet(username, password)
        
        # Navigate
        bot.page.goto("http://123nhadatviet.com/dang-tin.html", wait_until="domcontentloaded")
        time.sleep(2)
        
        # Fill Title & Content
        bot.page.fill("#tieude", mock_item["title"])
        bot.page.fill("#noidung", mock_item["content"])
        bot.page.select_option("#loaitin", "2")
        bot.page.select_option("#loaibds", "6")
        bot.page.select_option("#tinh", "3")
        time.sleep(1.5)
        
        # Fill Location using JS selects (district: 584)
        bot.page.evaluate("() => { const el = document.getElementById('huyen'); if(el) { el.value = '584'; el.dispatchEvent(new Event('change')); } }")
        time.sleep(2)
        
        # Select ward: Phường Hòa Cường Bắc (1093) or Hòa Cường Nam (1094)
        bot.page.evaluate("() => { const el = document.getElementById('phuong'); if(el) { el.value = '1093'; el.dispatchEvent(new Event('change')); } }")
        time.sleep(1)
        
        # Select street: Đường 2/9 (9654)
        bot.page.evaluate("() => { const el = document.getElementById('duong'); if(el) { el.value = '9654'; el.dispatchEvent(new Event('change')); } }")
        time.sleep(1)
        
        bot.page.fill("#diachi", mock_item["address"])
        bot.page.fill("#dientich", mock_item["area"])
        bot.page.fill("#gia", mock_item["price"])
        bot.page.select_option("#cachtinh", "1")
        
        bot.page.fill("#lienhe", mock_item["contact_name"])
        bot.page.fill("#dienthoai", mock_item["phone"])
        
        # Solve captcha using local OCR
        captcha_code = bot.solve_image_captcha_local(bot.page, "img.captchagenerator")
        print(f"Solved Captcha: {captcha_code}")
        if captcha_code:
            bot.page.fill("#captcha", captcha_code)
            
        # Click submit
        print("Clicking submit...")
        submit_btn = bot.page.locator("input[type='submit'], button:has-text('Đăng tin'), input[value='Đăng tin'], a:has-text('Đăng tin')").first
        submit_btn.click()
        
        # Wait for submission iframe to load
        print("Waiting for response inside iframe...")
        time.sleep(6)
        
        # Read iframe content
        iframe_html = bot.page.evaluate("""() => {
            const frame = document.getElementById('post_target');
            if (!frame) return 'No iframe found';
            try {
                const doc = frame.contentDocument || frame.contentWindow.document;
                return doc ? doc.body.innerHTML : 'No document inside iframe';
            } catch (e) {
                return 'Cross-origin error or access blocked: ' + e.message;
            }
        }""")
        print("Iframe content HTML:")
        print(iframe_html)
        
    except Exception as e:
        print("Error:", e)
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
