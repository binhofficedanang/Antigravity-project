import time
from playwright.sync_api import sync_playwright
import json

def test_login():
    with open('config.json', 'r') as f:
        config = json.load(f)
    username = config['rongbay.com']['username']
    password = config['rongbay.com']['password']

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        print("Mở trang rongbay.com...")
        page.goto("https://rongbay.com/", wait_until="commit")
        time.sleep(5)
        try:
            page.screenshot(path="rongbay_loaded.png", timeout=5000)
        except Exception as e:
            print("Không chụp được ảnh loaded (do timeout font):", e)
        
        print("Click nút Đăng nhập...")
        # Sử dụng class .hm_link_login
        try:
            # Hãy thử lấy selector a.hm_link_login hoặc click bằng JS trực tiếp
            page.evaluate("document.querySelector('a.hm_link_login').click()")
            print("Đã click a.hm_link_login qua JS")
            time.sleep(5)
            try:
                page.screenshot(path="rongbay_clicked.png", timeout=5000)
            except Exception as esc:
                print("Không chụp được ảnh clicked:", esc)
        except Exception as e:
            print("Lỗi click a.hm_link_login qua JS:", e)
            
            # Thử click bằng text
            try:
                page.click("text=Đăng nhập", timeout=5000)
                print("Đã click text=Đăng nhập")
                time.sleep(5)
                try:
                    page.screenshot(path="rongbay_clicked_text.png", timeout=5000)
                except Exception as esc2:
                    print("Không chụp được ảnh text clicked:", esc2)
            except Exception as e2:
                print("Lỗi click text=Đăng nhập:", e2)

        # Xem có iframe xuất hiện không
        print("Các frame hiện có:")
        for idx, frame in enumerate(page.frames):
            print(f"Frame {idx}: URL={frame.url}")
            if "vietid" in frame.url or "login" in frame.url:
                print("Tìm thấy frame VietID/Login!")
                try:
                    # Chụp ảnh nội dung trong frame
                    frame_body = frame.locator("body")
                    if frame_body.count() > 0:
                        print("Frame body is visible.")
                except Exception as ef:
                    print("Lỗi frame:", ef)

        browser.close()

if __name__ == "__main__":
    test_login()
