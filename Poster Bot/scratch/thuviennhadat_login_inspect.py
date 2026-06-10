import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Lắng nghe các request
        def handle_request(request):
            if "login" in request.url.lower() or "signin" in request.url.lower() or "user" in request.url.lower():
                print(f"\n[REQUEST] URL: {request.url}")
                print(f"Method: {request.method}")
                try:
                    if request.post_data:
                        print(f"Post Data: {request.post_data}")
                except Exception as e:
                    pass

        page.on("request", handle_request)
        
        # Lắng nghe response
        def handle_response(response):
            if "login" in response.url.lower() or "signin" in response.url.lower() or "user" in response.url.lower():
                print(f"[RESPONSE] URL: {response.url}")
                print(f"Status: {response.status}")
                try:
                    print(f"Text: {response.text()[:500]}")
                except Exception as e:
                    pass

        page.on("response", handle_response)

        print("Đang mở trang đăng nhập...")
        page.goto("https://thuviennhadat.vn/Users/Login?returnUrl=%2Fdang-tin", wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)
        
        print("Điền tài khoản...")
        page.fill("input#phone-mail-login-view", "0935723727")
        page.fill("input#password-login-view", "Binh1995@")
        
        print("Click Đăng nhập...")
        page.click("button#button-submit-login-view")
        time.sleep(6)
        
        browser.close()

if __name__ == "__main__":
    main()
