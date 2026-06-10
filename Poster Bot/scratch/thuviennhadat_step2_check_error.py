import time
import json
from playwright.sync_api import sync_playwright

def select_semantic_ui_dropdown(page, dropdown_selector, search_text):
    print(f"Chọn dropdown {dropdown_selector} với giá trị '{search_text}'...")
    page.click(dropdown_selector)
    time.sleep(1)
    page.fill(f"{dropdown_selector} input.search", search_text)
    time.sleep(2)
    page.keyboard.press("Enter")
    time.sleep(1)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
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

        print("Đang mở trang đăng nhập...")
        page.goto("https://thuviennhadat.vn/Users/Login?returnUrl=%2Fdang-tin", wait_until="domcontentloaded")
        time.sleep(3)
        page.fill("input#phone-mail-login-view", "0935723727")
        page.fill("input#password-login-view", "Binh1995@")
        page.click("button#button-submit-login-view")
        page.wait_for_url("**/dang-tin**")
        time.sleep(3)
        
        # Đóng modal welcome nếu có
        try:
            if page.locator("div.header:has-text('Chào mừng')").is_visible():
                page.click("i.close.icon")
                time.sleep(1)
        except Exception:
            pass
            
        page.click(".tag._post-transaction-type._rent")
        time.sleep(1)
        
        page.click("input[name='PostFullAddress']")
        time.sleep(2)
        select_semantic_ui_dropdown(page, "div.ui.search.dropdown._input-city", "Đà Nẵng")
        select_semantic_ui_dropdown(page, "div.ui.search.dropdown._input-dictrict", "Quận Hải Châu")
        select_semantic_ui_dropdown(page, "div.ui.search.dropdown._input-ward", "Phường Bình Thuận")
        page.fill("input[name='AddressName']", "Nguyễn Văn Linh")
        time.sleep(1)
        page.click("._btn-submit-location-picking")
        time.sleep(2)
        
        select_semantic_ui_dropdown(page, "div.ui.search.dropdown._input-post-category", "Văn phòng")
        page.fill("input[name='PostArea']", "100")
        page.fill("input[name='PostPrice']", "330000")
        
        # Chọn đơn vị giá
        page.click("div.ui.search.dropdown._input-post-price-type")
        time.sleep(1)
        page.click("div.ui.search.dropdown._input-post-price-type div.item[data-value='2']")
        time.sleep(1)
        
        page.fill("textarea[name='PostTitle']", "Cho thuê văn phòng Nguyễn Văn Linh, Hải Châu cực đẹp diện tích 100m2 giá tốt")
        page.fill("textarea[name='PostDescription']", "Cho thuê văn phòng đẹp tọa lạc trên đường Nguyễn Văn Linh, quận Hải Châu, Đà Nẵng.\nDiện tích sử dụng 100m2.\nVăn phòng rộng rãi, đầy đủ ánh sáng tự nhiên.\nLiên hệ ngay để xem thực tế!")
        
        print("Click Tiếp tục sang bước 2...")
        page.click(".next-step-btn")
        time.sleep(4)
        
        # Check lỗi trên trang
        errors = page.evaluate("""
            () => {
                let errs = [];
                // Check các element có class error hoặc invalid đang hiển thị
                document.querySelectorAll('.error, .invalid, .message.error, .ui.error.message').forEach(el => {
                    if (el.offsetWidth > 0 && el.offsetHeight > 0) {
                        errs.push({
                            class: el.className,
                            text: el.innerText
                        });
                    }
                });
                // Check các input bị viền đỏ hoặc có lỗi
                document.querySelectorAll('.field.error').forEach(el => {
                    errs.push({
                        class: el.className,
                        text: el.querySelector('label') ? el.querySelector('label').innerText : 'Field error'
                    });
                });
                return errs;
            }
        """)
        
        print("\nCác lỗi phát hiện được trên form:")
        for err in errors:
            print(f"Class: '{err['class']}' | Text: '{err['text']}'")
            
        # Chụp toàn bộ trang (full_page=True) để xem có gì khuất màn hình
        page.screenshot(path="thuviennhadat_step1_errors.png", full_page=True)
        print("Đã chụp toàn bộ trang vào thuviennhadat_step1_errors.png")
        
        browser.close()

if __name__ == "__main__":
    main()
