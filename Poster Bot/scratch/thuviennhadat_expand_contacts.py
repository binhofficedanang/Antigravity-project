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
        time.sleep(4)
        
        # Đóng modal welcome nếu có
        try:
            if page.locator("div.header:has-text('Chào mừng')").is_visible():
                page.click("i.close.icon")
                time.sleep(1)
        except Exception:
            pass
            
        # Click accordion Thông tin liên hệ
        print("Click tiêu đề accordion Thông tin liên hệ...")
        page.click("div.post-detail-accordion[data-type='contacts'] div.title")
        time.sleep(1.5)
        
        # Click Thêm liên hệ
        print("Click nút Thêm liên hệ...")
        page.click("._btn-contact-adding")
        time.sleep(2)
        
        # Chụp ảnh màn hình
        page.screenshot(path="thuviennhadat_contacts_expanded.png")
        print("Đã chụp ảnh vào thuviennhadat_contacts_expanded.png")
        
        # Xem HTML phần này
        html_content = page.locator("div.post-detail-accordion[data-type='contacts']").inner_html()
        with open("thuviennhadat_contacts_expanded.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Đã lưu HTML thuviennhadat_contacts_expanded.html")
        
        browser.close()

if __name__ == "__main__":
    main()
