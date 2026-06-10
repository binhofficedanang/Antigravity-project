import os
import re
import time
from playwright.sync_api import sync_playwright

def register():
    print("🚀 Khởi động đăng ký tài khoản trên muabandanang.vn (Phiên bản cải tiến)...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    session_dir = os.path.join(base_dir, "browser_sessions")
    
    username = "binhofficedanang"
    email = "binh.officedanang@gmail.com"
    password = "Binh1995@"
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            headless=True,
            args=["--start-maximized"]
        )
        page = browser.new_page()
        try:
            # Lặp để lấy phép tính dương cho an toàn
            for attempt in range(5):
                page.goto("https://muabandanang.vn/dang-ky", timeout=30000)
                page.wait_for_timeout(3000)
                
                captcha_label_el = page.locator("#captcha").locator("xpath=preceding-sibling::label | parent::*//label").first
                if captcha_label_el.is_visible():
                    captcha_text = captcha_label_el.inner_text()
                    m = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', captcha_text)
                    if m:
                        val1 = int(m.group(1))
                        op = m.group(2)
                        val2 = int(m.group(3))
                        
                        # Đảm bảo kết quả phép tính >= 0
                        if op == '-' and val1 < val2:
                            print(f"Phép tính âm ({val1} - {val2}), tải lại trang...")
                            continue
                        break
            
            # Fill registration fields robustly
            page.locator("#username").click()
            page.locator("#username").fill("")
            page.locator("#username").type(username, delay=50)
            
            page.locator("#email").click()
            page.locator("#email").fill("")
            page.locator("#email").type(email, delay=50)
            
            page.locator("#pwd1").click()
            page.locator("#pwd1").fill("")
            page.locator("#pwd1").type(password, delay=50)
            
            page.locator("#pwd2").click()
            page.locator("#pwd2").fill("")
            page.locator("#pwd2").type(password, delay=50)
            
            # Solve math captcha
            captcha_label_el = page.locator("#captcha").locator("xpath=preceding-sibling::label | parent::*//label").first
            if captcha_label_el.is_visible():
                captcha_text = captcha_label_el.inner_text()
                print("Math Captcha:", captcha_text)
                
                m = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', captcha_text)
                if m:
                    val1 = int(m.group(1))
                    op = m.group(2)
                    val2 = int(m.group(3))
                    
                    if op == '+':
                        ans = val1 + val2
                    elif op == '-':
                        ans = val1 - val2
                    elif op == '*':
                        ans = val1 * val2
                    else:
                        ans = 0
                        
                    print(f"Calculated answer: {val1} {op} {val2} = {ans}")
                    page.locator("#captcha").click()
                    page.locator("#captcha").fill("")
                    page.locator("#captcha").type(str(ans), delay=50)
                else:
                    print("Could not parse equation from text:", captcha_text)
                    
            page.screenshot(path="mbdn_before_submit.png")
            
            # Submit form
            page.click("button[type='submit']:has-text('ĐĂNG KÝ')")
            page.wait_for_timeout(5000)
            
            page.screenshot(path="mbdn_after_submit.png")
            print("Registration submitted. Current URL:", page.url)
            
            body_text = page.locator("body").inner_text()
            if "đăng ký thành công" in body_text.lower() or "thành công" in body_text.lower():
                print("🎉 Đăng ký tài khoản trên muabandanang.vn THÀNH CÔNG!")
            elif "tên đăng nhập đã tồn tại" in body_text.lower() or "email đã tồn tại" in body_text.lower() or "đã được đăng ký" in body_text.lower():
                print("ℹ️ Tài khoản đã tồn tại hoặc đã đăng ký thành công trước đó.")
            else:
                print("⚠️ Trạng thái không rõ ràng, có thể cần kiểm tra screenshot mbdn_after_submit.png")
        except Exception as e:
            print("❌ Lỗi đăng ký:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    register()
