import time
import json
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Intercept login request
        def route_handler(route):
            request = route.request
            if request.method == "POST" and "Users/Login" in request.url:
                try:
                    data = request.post_data_json
                    if data.get("PhoneNumber") == "0935723727":
                        data["PhoneNumber"] = "84935723727"
                    route.continue_(post_data=json.dumps(data))
                except Exception:
                    route.continue_()
            else:
                route.continue_()
                
        page.route("**/Users/Login", route_handler)

        print("Đang đăng nhập...")
        page.goto("https://thuviennhadat.vn/Users/Login?returnUrl=%2Fdang-tin", wait_until="domcontentloaded")
        page.fill("input#phone-mail-login-view", "0935723727")
        page.fill("input#password-login-view", "Binh1995@")
        page.click("button#button-submit-login-view")
        page.wait_for_url("**/dang-tin**")
        time.sleep(5)
        
        # Đóng modal welcome nếu có
        try:
            if page.locator("div.header:has-text('Chào mừng')").is_visible():
                page.click("i.close.icon")
                time.sleep(1)
        except Exception:
            pass
            
        # Tìm element _btn-contact-adding
        btn_exists = page.evaluate('!!document.querySelector("._btn-contact-adding")')
        print(f"Nút _btn-contact-adding có tồn tại không: {btn_exists}")
        
        if btn_exists:
            # Click bằng JS evaluate
            print("Đang click nút thêm liên hệ bằng JS evaluate...")
            page.evaluate('document.querySelector("._btn-contact-adding").click()')
            time.sleep(3)
            
            # Kiểm tra xem có cấu trúc HTML mới nào xuất hiện không
            contact_html = page.evaluate('document.querySelector("._group-contact-information").innerHTML')
            print("\n=== Inner HTML của _group-contact-information sau khi click ===")
            print(contact_html)
            print("==========================================================")
            
            page.screenshot(path="thuviennhadat_after_js_click.png", full_page=True)
            print("Đã chụp ảnh toàn trang vào thuviennhadat_after_js_click.png")
            
        browser.close()

if __name__ == "__main__":
    main()
