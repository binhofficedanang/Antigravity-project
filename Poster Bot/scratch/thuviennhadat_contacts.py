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
        
        # In inner HTML của _group-contact-information
        contact_html = page.evaluate('document.querySelector("._group-contact-information").innerHTML')
        print("\n=== Inner HTML của _group-contact-information ===")
        print(contact_html)
        print("=================================================")
        
        # Xem có bao nhiêu liên hệ hiển thị và thông tin của chúng
        contacts = page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('._group-contact-information .item')).map(item => {
                    return {
                        text: item.innerText,
                        html: item.outerHTML
                    };
                });
            }
        """)
        
        print(f"\nSố lượng liên hệ tìm thấy: {len(contacts)}")
        for idx, contact in enumerate(contacts):
            print(f"Liên hệ #{idx + 1}: {contact['text']}")
            
        browser.close()

if __name__ == "__main__":
    main()
