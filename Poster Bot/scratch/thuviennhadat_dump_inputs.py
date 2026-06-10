import time
import random
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print("Đang mở trang đăng nhập...")
        page.goto("https://thuviennhadat.vn/Users/Login?returnUrl=%2Fdang-tin", wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)
        
        print("Chuyển sang tab Đăng ký...")
        page.click("#register-view")
        time.sleep(2)
        
        phone_num = "098" + "".join([str(random.randint(0, 9)) for _ in range(7)])
        print(f"Điền số điện thoại: {phone_num}")
        page.fill("input#phone-mail-login", phone_num)
        
        # Chụp ảnh bước 1
        page.screenshot(path="thuviennhadat_register_step1.png")
        
        print("Click Tiếp tục...")
        page.click("button#button-submit-login")
        time.sleep(4)
        
        # Chụp ảnh bước 2
        page.screenshot(path="thuviennhadat_register_step2.png")
        print("Đã chụp ảnh bước 2 vào thuviennhadat_register_step2.png")
        
        # Lấy thông tin tất cả inputs
        inputs = page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('input')).map(input => ({
                    id: input.id,
                    name: input.name,
                    type: input.type,
                    value: input.value,
                    placeholder: input.placeholder,
                    visible: input.offsetWidth > 0 && input.offsetHeight > 0
                }));
            }
        """)
        
        print("\n=== DANH SÁCH INPUTS TRÊN TRANG ===")
        for i, inp in enumerate(inputs):
            print(f"{i}. ID: '{inp['id']}' | Name: '{inp['name']}' | Type: '{inp['type']}' | Visible: {inp['visible']} | Placeholder: '{inp['placeholder']}'")
            
        browser.close()

if __name__ == "__main__":
    main()
