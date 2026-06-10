import time
import json
import os
from playwright.sync_api import sync_playwright

# Tạo 3 ảnh dummy 100x100 pixel để test upload
def create_dummy_images():
    print("Tạo các ảnh test dummy...")
    from PIL import Image
    os.makedirs("scratch", exist_ok=True)
    img_paths = []
    colors = ["red", "green", "blue"]
    for idx, color in enumerate(colors):
        path = os.path.abspath(f"scratch/test_img_{idx + 1}.png")
        img = Image.new("RGB", (300, 300), color=color)
        img.save(path)
        img_paths.append(path)
    return img_paths

def select_semantic_ui_dropdown(page, dropdown_selector, search_text):
    print(f"Chọn dropdown {dropdown_selector} với giá trị '{search_text}'...")
    page.click(dropdown_selector)
    time.sleep(1)
    page.fill(f"{dropdown_selector} input.search", search_text)
    time.sleep(2)
    page.keyboard.press("Enter")
    time.sleep(1)

def main():
    img_paths = create_dummy_images()
    
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
        select_semantic_ui_dropdown(page, "div.ui.search.dropdown._input-dictrict", "Quận Hải Châu")
        select_semantic_ui_dropdown(page, "div.ui.search.dropdown._input-ward", "Phường Bình Thuận")
        page.fill("input[name='AddressName']", "Nguyễn Văn Linh")
        time.sleep(1)
        page.click("._btn-submit-location-picking")
        time.sleep(2)
        
        # Chọn Loại Nhà Đất
        select_semantic_ui_dropdown(page, "div.ui.search.dropdown._input-post-category", "Văn phòng")
        
        # Nhập diện tích, giá
        page.fill("input[name='PostArea']", "100")
        page.fill("input[name='PostPrice']", "330000")
        
        # Chọn đơn vị giá
        page.click("div.ui.search.dropdown._input-post-price-type")
        time.sleep(1)
        page.click("div.ui.search.dropdown._input-post-price-type div.item[data-value='2']")
        time.sleep(1)
        
        # Add Contact
        print("Thêm liên hệ...")
        page.evaluate('document.querySelector("._btn-contact-adding").click()')
        time.sleep(2)
        page.fill("input._input-contact-name", "Nguyễn Văn Bình")
        page.fill("input._input-contact-phone", "0935723727")
        page.click("._modal-contact-adding .ui.checkbox label")
        time.sleep(1)
        page.click("._btn-submit-contact-adding")
        time.sleep(2)
        
        # Nhập tiêu đề & mô tả
        page.fill("textarea[name='PostTitle']", "Cho thuê văn phòng Nguyễn Văn Linh, Hải Châu cực đẹp diện tích 100m2 giá tốt")
        page.fill("textarea[name='PostDescription']", "Cho thuê văn phòng đẹp tọa lạc trên đường Nguyễn Văn Linh, quận Hải Châu, Đà Nẵng.\nDiện tích sử dụng 100m2.\nVăn phòng rộng rãi, đầy đủ ánh sáng tự nhiên.\nLiên hệ ngay để xem thực tế!")
        
        # Click Tiếp tục
        print("Click Tiếp tục sang bước 2...")
        page.click(".next-step-btn")
        time.sleep(5)
        
        # Upload 3 ảnh thường
        print("Đang upload 3 ảnh test lên input file...")
        page.set_input_files("input#_input-post-images", img_paths)
        time.sleep(6) # Chờ upload và hiển thị preview
        
        # Chụp ảnh bước 2 đã upload xong ảnh
        page.screenshot(path="thuviennhadat_step2_uploaded.png", full_page=True)
        print("Đã chụp ảnh bước 2 đã upload xong ảnh vào thuviennhadat_step2_uploaded.png")
        
        # Click Tiếp tục sang bước 3
        print("Click Tiếp tục sang bước 3...")
        page.click(".next-step-btn")
        time.sleep(6)
        
        # Chụp màn hình trang bước 3
        page.screenshot(path="thuviennhadat_step3.png", full_page=True)
        print("Đã chụp màn hình trang Bước 3 vào thuviennhadat_step3.png")
        
        # Lưu HTML trang bước 3
        html_content = page.content()
        with open("thuviennhadat_step3.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Đã lưu cấu trúc HTML trang Bước 3 thành công vào thuviennhadat_step3.html")
        
        browser.close()

if __name__ == "__main__":
    main()
