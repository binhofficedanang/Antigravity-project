import time
from playwright.sync_api import sync_playwright
import os

def test():
    with sync_playwright() as p:
        print("Mở persistent context với channel='chrome'...")
        user_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../browser_sessions_test")
        
        # 1. Launch context
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=True,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-infobars",
                "--window-size=1280,800",
                "--disable-gpu-sandbox",
            ],
            ignore_default_args=["--enable-automation"],
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="vi-VN",
            timezone_id="Asia/Ho_Chi_Minh",
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        
        # Apply stealth
        try:
            from playwright_stealth import stealth_sync
            stealth_sync(page)
            print("playwright-stealth applied")
        except Exception as e:
            print("playwright-stealth failed:", e)
            
        print("Mở trang login muaban.net...")
        page.goto("https://muaban.net/account/login", wait_until="domcontentloaded")
        
        # Đợi 15s xem có qua được không
        for i in range(15):
            print(f"Giây {i+1}: URL={page.url}, Title={page.title()}")
            time.sleep(1)
            
        # Take screenshot
        page.screenshot(path="muaban_cf_test.png")
        print("Đã chụp muaban_cf_test.png")
        
        context.close()

if __name__ == "__main__":
    test()
