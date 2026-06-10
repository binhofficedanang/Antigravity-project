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
    
    # Listen to console messages
    bot.page.on("console", lambda msg: print(f"🖥️ Console [{msg.type}]: {msg.text}"))
    
    # Listen to page errors
    bot.page.on("pageerror", lambda err: print(f"❌ Page Error: {err}"))
    
    # Listen to dialog event
    def handle_dialog(dialog):
        print(f"🚨 Dialog popped up: {dialog.type} - Message: '{dialog.message}'")
        dialog.dismiss()
    bot.page.on("dialog", handle_dialog)
    
    try:
        # Login
        bot.login_123nhadatviet(username, password)
        
        # Navigate
        bot.page.goto("http://123nhadatviet.com/dang-tin.html", wait_until="domcontentloaded")
        time.sleep(2)
        
        # Fill Title & Content
        bot.page.fill("#tieude", "Cho thuê văn phòng 35m2 cực đẹp quận Hải Châu Đà Nẵng")
        bot.page.fill("#noidung", "Cần cho thuê văn phòng diện tích 35m2 tại trung tâm quận Hải Châu, Đà Nẵng. Không gian rộng rãi, thoáng mát, đầy đủ tiện ích và ánh sáng tự nhiên tốt, thích hợp làm văn phòng đại diện hoặc công ty khởi nghiệp.")
        bot.page.select_option("#loaitin", "2")
        bot.page.select_option("#loaibds", "6")
        bot.page.select_option("#tinh", "3")
        time.sleep(1.5)
        
        # Fill Location using JS selects (district: 584)
        bot.page.evaluate("() => { const el = document.getElementById('huyen'); if(el) { el.value = '584'; el.dispatchEvent(new Event('change')); } }")
        time.sleep(2)
        
        # Select ward: Phường Hòa Cường Bắc (1093)
        bot.page.evaluate("() => { const el = document.getElementById('phuong'); if(el) { el.value = '1093'; el.dispatchEvent(new Event('change')); } }")
        time.sleep(1)
        
        # Select street: Đường 2/9 (9654)
        bot.page.evaluate("() => { const el = document.getElementById('duong'); if(el) { el.value = '9654'; el.dispatchEvent(new Event('change')); } }")
        time.sleep(1)
        
        bot.page.fill("#diachi", "đường 2/9, Hải Châu, Đà Nẵng")
        bot.page.fill("#dientich", "35")
        bot.page.fill("#gia", "7000")
        bot.page.select_option("#cachtinh", "1")
        
        bot.page.fill("#lienhe", "Nguyễn Ngọc Thiên Bình")
        bot.page.fill("#dienthoai", "0935723727")
        
        # Solve captcha
        captcha_code = bot.solve_image_captcha_local(bot.page, "img.captchagenerator")
        print(f"Solved Captcha: {captcha_code}")
        if captcha_code:
            bot.page.fill("#captcha", captcha_code)
            
        # Capture form screenshot
        bot.safe_screenshot("debug_form_before_submit.png")
        
        # Let's inspect the values of fields before clicking
        form_vals = bot.page.evaluate("""() => {
            return {
                tieude: document.getElementById('tieude').value,
                noidung: document.getElementById('noidung').value,
                loaitin: document.getElementById('loaitin').value,
                loaibds: document.getElementById('loaibds').value,
                tinh: document.getElementById('tinh').value,
                huyen: document.getElementById('huyen').value,
                phuong: document.getElementById('phuong').value,
                duong: document.getElementById('duong').value,
                diachi: document.getElementById('diachi').value,
                dientich: document.getElementById('dientich').value,
                gia: document.getElementById('gia').value,
                captcha: document.getElementById('captcha').value
            };
        }""")
        print("Form values before click:", form_vals)
        
        # Click submit
        print("Clicking span.update...")
        bot.page.click("span.update")
        
        # Wait a few seconds
        time.sleep(5)
        
        # Capture screenshot after submit
        bot.safe_screenshot("debug_form_after_submit.png")
        
        # Print final URL
        print("Final URL:", bot.page.url)
        
    except Exception as e:
        print("Error:", e)
    finally:
        bot.stop()

if __name__ == '__main__':
    main()
