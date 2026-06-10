import time
import os
import json
import csv
import argparse
from playwright.sync_api import sync_playwright

def load_config(filepath="config.json"):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def load_data(filepath="data.csv"):
    data = []
    if not os.path.exists(filepath):
        return data
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def load_selectors(site_name, filepath="selectors_db.json"):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        db = json.load(f)
    return db.get(site_name)

def get_property_images(property_title):
    import re
    safe_title = re.sub(r'[^\w\-_\. ]', '', property_title).strip().replace(' ', '_')
    download_dir = os.path.abspath(os.path.join("downloads", safe_title))
    if os.path.exists(download_dir):
        files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        return files
    return []

def main():
    parser = argparse.ArgumentParser(description="Hybrid Playwright Runner")
    parser.add_argument("-s", "--site", type=str, default="raovat.net",
                        help="Trang web muốn đăng tin (mặc định: raovat.net)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Chế độ chạy thử, điền form nhưng không nhấn gửi bài")
    parser.add_argument("--headless", action="store_true",
                        help="Chạy ẩn danh")
    args = parser.parse_args()

    print(f"=== BẮT ĐẦU CHẠY TRÌNH ĐĂNG TIN THUẦN PLAYWRIGHT (TRANG: {args.site}) ===")

    # 1. Tải selectors của trang
    selectors = load_selectors(args.site)
    if not selectors:
        print(f"❌ Lỗi: Chưa có selectors cho trang [{args.site}] trong selectors_db.json.")
        print(f"👉 Vui lòng chạy lệnh quét AI trước: python ai_selector_generator.py --site {args.site}")
        return

    # 2. Tải cấu hình tài khoản & dữ liệu bài đăng
    config = load_config()
    site_config = config.get(args.site)
    if not site_config:
        print(f"❌ Không tìm thấy thông tin tài khoản cho trang {args.site} trong config.json")
        return
        
    username = site_config.get("username")
    email = site_config.get("email")
    phone = site_config.get("phone")
    password = site_config.get("password")
    
    # Quyết định tài khoản điền vào form: chọn Email nếu selector là email, hoặc SĐT, hoặc Username
    login_credential = email or username or phone
    
    # 3. Lấy bài đăng mẫu
    data = load_data()
    if not data:
        print("❌ Dữ liệu đăng tin rỗng (data.csv)")
        return
    item = data[0]
    
    # 4. Khởi chạy Playwright thuần
    print("🚀 Đang khởi chạy Playwright...")
    with sync_playwright() as p:
        # Sử dụng Persistent Context để giữ session cookies
        user_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_sessions")
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=args.headless,
            viewport={"width": 1280, "height": 800},
            ignore_default_args=["--enable-automation"],
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        
        # --- BƯỚC 1: Đăng nhập ---
        login_url = selectors.get("login_url")
        print(f"🔗 Đi tới trang đăng nhập: {login_url}")
        page.goto(login_url, wait_until="domcontentloaded")
        time.sleep(2)
        
        # Điền form đăng nhập
        try:
            email_sel = selectors.get("email_input")
            pass_sel = selectors.get("password_input")
            submit_sel = selectors.get("login_submit")
            
            # Chọn loại tài khoản phù hợp (nếu email_input là email hoặc chứa chữ email, ưu tiên điền email)
            # Đối với các trang Việt Nam, AI sẽ chọn đúng selector.
            print(f"⌨️  Điền tài khoản: {login_credential}")
            page.fill(email_sel, login_credential)
            page.fill(pass_sel, password)
            
            print("🖱️  Click Đăng nhập")
            page.click(submit_sel)
            time.sleep(5) # Chờ chuyển hướng
        except Exception as e:
            print(f"⚠️ Có lỗi trong quá trình điền thông tin đăng nhập: {e}. Thử tiếp tục...")

        # --- BƯỚC 2: Đi tới trang đăng tin ---
        post_url = selectors.get("post_url")
        print(f"🔗 Đi tới trang đăng tin: {post_url}")
        page.goto(post_url, wait_until="domcontentloaded")
        time.sleep(3)
        
        # Đóng popup thông báo nếu có (ví dụ: nút Cancel trên raovat.net)
        try:
            # Tự động đóng popup thông báo nếu phát hiện các nút hủy/đóng phổ biến
            for close_sel in ["#btnCancelNotification", ".close", "button:has-text('Cancel')", "button:has-text('Đóng')"]:
                if page.locator(close_sel).is_visible():
                    page.click(close_sel)
                    print(f"✓ Đã tự động đóng popup: {close_sel}")
                    time.sleep(1)
        except Exception:
            pass

        # --- BƯỚC 3: Chọn danh mục (category_clicks) ---
        category_clicks = selectors.get("category_clicks", [])
        if category_clicks:
            print(f"📁 Thực hiện chọn danh mục qua {len(category_clicks)} click chuột...")
            for idx, click_sel in enumerate(category_clicks):
                try:
                    print(f"  - Click {idx+1}: {click_sel}")
                    page.click(click_sel)
                    time.sleep(1.5)
                except Exception as e_click:
                    print(f"  ❌ Lỗi khi click {click_sel}: {e_click}")

        # --- BƯỚC 4: Điền thông tin bài đăng ---
        print("✍️ Đang điền form bài viết...")
        try:
            if selectors.get("title_input"):
                print(f"  - Điền tiêu đề: {item.get('title')}")
                page.fill(selectors.get("title_input"), item.get("title"))
            if selectors.get("content_textarea"):
                print("  - Điền nội dung chi tiết...")
                page.fill(selectors.get("content_textarea"), item.get("content"))
            
            # Xử lý giá tiền (chỉ lấy số thô nếu form yêu cầu số)
            if selectors.get("price_input"):
                raw_price = item.get("price")
                numeric_price = "".join(c for c in raw_price if c.isdigit())
                if not numeric_price:
                    numeric_price = "0"
                print(f"  - Điền giá: {numeric_price}")
                page.fill(selectors.get("price_input"), numeric_price)
            
            # Điền diện tích
            if selectors.get("area_input"):
                print(f"  - Điền diện tích: {item.get('area')}")
                page.fill(selectors.get("area_input"), item.get("area"))
            
            # --- BƯỚC 5: Tải hình ảnh ---
            images = get_property_images(item.get("title"))
            if images and selectors.get("image_upload"):
                print(f"🖼️ Tải lên {len(images)} hình ảnh...")
                page.locator(selectors.get("image_upload")).set_input_files(images)
                time.sleep(3) # Chờ load ảnh
                
        except Exception as e_fill:
            print(f"❌ Lỗi khi điền thông tin đăng tin: {e_fill}")

        # --- BƯỚC 6: Hoàn tất hoặc Dry-run ---
        screenshot_path = f"debug_{args.site}_form_filled.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Đã chụp ảnh màn hình lưu tại: {screenshot_path}")
        
        if args.dry_run:
            print("\n✓ [CHẾ ĐỘ DRY-RUN] Đã điền form đăng tin thành công. Dừng lại trước khi gửi bài!")
        else:
            print("\n🚀 Bấm gửi bài đăng...")
            try:
                page.click(selectors.get("submit_button"))
                time.sleep(5)
                print("✓ Đăng tin thành công!")
            except Exception as e_submit:
                print(f"❌ Lỗi khi nhấn nút đăng tin: {e_submit}")
                
        context.close()
        print("🏁 Hoàn thành trình đăng tin.")

if __name__ == "__main__":
    main()
