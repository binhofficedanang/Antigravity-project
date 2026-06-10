import os
import time
from playwright.sync_api import sync_playwright
import json

def test_login_rongbay():
    with open('config.json', 'r') as f:
        config = json.load(f)
        
    username = config['rongbay.com']['username']
    password = config['rongbay.com']['password']
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        print(f"Đang đăng nhập rongbay.com với tài khoản: {username}")
        page.goto("https://rongbay.com/", wait_until="domcontentloaded")
        time.sleep(2)
        
        # Click nút Đăng nhập góc trên
        try:
            page.click("a.login_header")
            print("  => Đã click mở popup đăng nhập")
            time.sleep(3)
            
            # Form login Rongbay sử dụng hệ thống id.rongbay.com hoặc VietID. Cần xác định selector chính xác
            # Lưu cấu trúc HTML để debug nếu lỗi
            page.screenshot(path="rongbay_login_popup.png")
            print("  => Đã lưu ảnh chụp popup đăng nhập")
            
            # Gửi text HTML popup để bot phân tích
            popup_html = page.evaluate("document.body.innerHTML")
            with open("rongbay_popup.html", "w", encoding="utf-8") as f:
                f.write(popup_html)
                
            # Thử gọi hàm thực sự trong web_automation (nhưng tách biệt script ra cho an toàn)
            # iframe VietID
            iframe = page.frame_locator("iframe[src*='vietid.net']")
            if iframe.locator("body").count() > 0:
                print("  => Đã tìm thấy iframe VietID")
                iframe.locator("input[name='email']").fill(username)
                iframe.locator("input[name='password']").fill(password)
                iframe.locator("#submitLogin").click()
                time.sleep(5)
                
                page.screenshot(path="rongbay_login_after_submit.png")
                print("  => Đã lưu ảnh sau submit")
                
                # Check url
                print(f"  => Current URL: {page.url}")
            else:
                print("  => KHÔNG tìm thấy iframe VietID. Cần kiểm tra rongbay_login_popup.png")
                
        except Exception as e:
            print(f"Lỗi: {e}")
            page.screenshot(path="rongbay_login_error.png")
            
        browser.close()

if __name__ == "__main__":
    test_login_rongbay()
