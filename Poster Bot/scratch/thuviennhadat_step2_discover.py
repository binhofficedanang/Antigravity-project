import time
from playwright.sync_api import sync_playwright

def select_semantic_ui_dropdown(page, dropdown_selector, search_text):
    print(f"Chọn dropdown {dropdown_selector} với giá trị '{search_text}'...")
    # Click dropdown để mở rộng
    page.click(dropdown_selector)
    time.sleep(1)
    # Gõ từ khóa tìm kiếm
    page.fill(f"{dropdown_selector} input.search", search_text)
    time.sleep(1.5)
    # Nhấn Enter để xác nhận lựa chọn
    page.keyboard.press("Enter")
    time.sleep(1)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
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
        
        print(f"URL hiện tại: {page.url}")
        
        # Nếu có modal welcome xuất hiện, đóng nó
        try:
            if page.locator("div.header:has-text('Chào mừng')").is_visible():
                print("Phát hiện modal chào mừng, đang đóng...")
                page.click("i.close.icon")
                time.sleep(1)
        except Exception as e:
            print("Không tìm thấy modal chào mừng hoặc có lỗi khi đóng:", e)
            
        # Chọn Nhu cầu: Cho thuê
        print("Chọn nhu cầu: Cho thuê...")
        page.click(".tag._post-transaction-type._rent")
        time.sleep(1)
        
        # Mở modal địa chỉ
        print("Mở modal Địa chỉ...")
        page.click("input[name='PostFullAddress']")
        time.sleep(2)
        
        # Chọn tỉnh: Đà Nẵng
        select_semantic_ui_dropdown(page, "div.ui.search.dropdown._input-city", "Đà Nẵng")
        
        # Chọn quận: Quận Hải Châu
        select_semantic_ui_dropdown(page, "div.ui.search.dropdown._input-dictrict", "Quận Hải Châu")
        
        # Chọn phường: Phường Bình Thuận
        select_semantic_ui_dropdown(page, "div.ui.search.dropdown._input-ward", "Phường Bình Thuận")
        
        # Nhập đường phố
        print("Nhập tên đường: Nguyễn Văn Linh...")
        page.fill("input[name='AddressName']", "Nguyễn Văn Linh")
        time.sleep(1)
        
        # Click Xác nhận
        print("Click Xác nhận địa chỉ...")
        page.click("._btn-submit-location-picking")
        time.sleep(2)
        
        # Chọn Loại Nhà Đất: Cho thuê văn phòng
        # Ta có thể tìm kiếm từ khóa "văn phòng" hoặc chọn mục tương ứng
        select_semantic_ui_dropdown(page, "div.ui.search.dropdown._input-post-category", "Văn phòng")
        
        # Nhập diện tích: 100
        print("Nhập diện tích: 100 m²...")
        page.fill("input[name='PostArea']", "100")
        
        # Nhập mức giá: 330000 VND/m2
        print("Nhập giá: 330000...")
        page.fill("input[name='PostPrice']", "330000")
        
        # Chọn đơn vị giá là VND/m2 (giá trị '2')
        print("Chọn đơn vị giá: VND/m²...")
        page.click("div.ui.search.dropdown._input-post-price-type")
        time.sleep(1)
        page.click("div.ui.search.dropdown._input-post-price-type div.item[data-value='2']")
        time.sleep(1)
        
        # Nhập tiêu đề
        print("Nhập tiêu đề...")
        page.fill("textarea[name='PostTitle']", "Cho thuê văn phòng Nguyễn Văn Linh, Hải Châu cực đẹp diện tích 100m2 giá tốt")
        
        # Nhập mô tả
        print("Nhập mô tả...")
        page.fill("textarea[name='PostDescription']", "Cho thuê văn phòng đẹp tọa lạc trên đường Nguyễn Văn Linh, quận Hải Châu, Đà Nẵng.\nDiện tích sử dụng 100m2.\nVăn phòng rộng rãi, đầy đủ ánh sáng tự nhiên.\nLiên hệ ngay để xem thực tế!")
        
        # Chụp ảnh bước 1 trước khi chuyển tiếp
        page.screenshot(path="thuviennhadat_step1_filled.png")
        print("Đã chụp ảnh bước 1 đã điền thông tin vào thuviennhadat_step1_filled.png")
        
        # Click nút Tiếp tục để sang bước 2
        print("Click Tiếp tục sang bước 2...")
        page.click(".next-step-btn")
        time.sleep(5)
        
        # Lưu HTML trang bước 2
        html_content = page.content()
        with open("thuviennhadat_step2.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Đã lưu cấu trúc HTML trang Bước 2 thành công vào thuviennhadat_step2.html")
        
        # Chụp màn hình trang bước 2
        page.screenshot(path="thuviennhadat_step2.png")
        print("Đã chụp màn hình trang Bước 2 vào thuviennhadat_step2.png")
        
        browser.close()

if __name__ == "__main__":
    main()
