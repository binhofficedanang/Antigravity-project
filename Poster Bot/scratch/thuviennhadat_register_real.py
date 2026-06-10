import time
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
        
        # Thử điền SĐT thật của người dùng: 0935723727
        print("Nhập số điện thoại đăng ký: 0935723727")
        page.fill("input#phone-regist-view", "0935723727")
        
        # Click tiếp tục
        print("Click Tiếp tục...")
        page.click("button#button-submit-regist-view")
        time.sleep(4)
        
        # Chụp ảnh màn hình để xem trang hiển thị gì tiếp theo (ví dụ: OTP hay mật khẩu trực tiếp)
        page.screenshot(path="thuviennhadat_register_real_step2.png")
        print("Đã chụp ảnh màn hình bước 2 vào thuviennhadat_register_real_step2.png")
        
        # Lấy tất cả input có thuộc tính hiển thị (visible)
        visible_inputs = page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('input'))
                    .filter(input => input.offsetWidth > 0 && input.offsetHeight > 0)
                    .map(input => ({
                        id: input.id,
                        placeholder: input.placeholder,
                        type: input.type
                    }));
            }
        """)
        
        print("\nCác input hiển thị ở bước 2:")
        for inp in visible_inputs:
            print(f"ID: '{inp['id']}' | Placeholder: '{inp['placeholder']}' | Type: '{inp['type']}'")
            
        browser.close()

if __name__ == "__main__":
    main()
