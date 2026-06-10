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
                print("\n[INTERCEPT] Bắt được request POST tới Users/Login!")
                try:
                    data = request.post_data_json
                    print(f"Payload gốc: {data}")
                    if data.get("PhoneNumber") == "0935723727":
                        data["PhoneNumber"] = "84935723727"
                        print(f"Payload sau khi sửa: {data}")
                    route.continue_(post_data=json.dumps(data))
                except Exception as e:
                    print("Lỗi khi sửa payload:", e)
                    route.continue_()
            else:
                route.continue_()
                
        page.route("**/Users/Login", route_handler)
        
        # Lắng nghe response
        def response_handler(response):
            if "Users/Login" in response.url and response.request.method == "POST":
                print(f"\n[RESPONSE] Status: {response.status}")
                try:
                    print(f"Response Text: {response.text()}")
                except Exception as e:
                    pass
        page.on("response", response_handler)

        print("Đang mở trang đăng nhập...")
        page.goto("https://thuviennhadat.vn/Users/Login?returnUrl=%2Fdang-tin", wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)
        
        print("Điền tài khoản...")
        page.fill("input#phone-mail-login-view", "0935723727")
        page.fill("input#password-login-view", "Binh1995@")
        
        print("Click Đăng nhập...")
        page.click("button#button-submit-login-view")
        
        # Chờ chuyển hướng sang trang dang-tin
        print("Chờ chuyển hướng sang dang-tin...")
        try:
            page.wait_for_url("**/dang-tin", timeout=15000)
            print("Đã chuyển hướng sang dang-tin thành công!")
        except Exception as e:
            print("Lỗi khi chờ chuyển hướng:", e)
            
        print(f"URL hiện tại: {page.url}")
        
        # Chụp màn hình sau khi login
        page.screenshot(path="thuviennhadat_login_route_result.png")
        print("Đã chụp ảnh thuviennhadat_login_route_result.png")
        
        browser.close()

if __name__ == "__main__":
    main()
