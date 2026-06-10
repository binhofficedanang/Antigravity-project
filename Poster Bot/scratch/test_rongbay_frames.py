import time
from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print("1. Mở trang rongbay.com...")
        page.goto("https://rongbay.com/", wait_until="commit")
        time.sleep(5)
        
        print("2. Click Đăng nhập...")
        try:
            page.evaluate("document.querySelector('a.hm_link_login').click()")
            print("   ✓ Đã click a.hm_link_login qua JS")
        except Exception as e:
            print("   ⚠️ Lỗi click:", e)
            
        time.sleep(10)
        print("3. Kiểm tra các frames và URL:")
        print("   URL hiện tại:", page.url)
        
        for idx, frame in enumerate(page.frames):
            print(f"\n--- Frame {idx} ---")
            print(f"  URL: {frame.url}")
            print(f"  Name: {frame.name}")
            
            try:
                inputs = frame.locator("input").all()
                print(f"  Inputs: {len(inputs)}")
                for inp in inputs:
                    print(f"    - name={inp.get_attribute('name')}, id={inp.get_attribute('id')}, type={inp.get_attribute('type')}")
                    
                buttons = frame.locator("button, input[type='submit']").all()
                print(f"  Buttons: {len(buttons)}")
                for btn in buttons:
                    print(f"    - name={btn.get_attribute('name')}, id={btn.get_attribute('id')}, text={btn.inner_text().strip()}")
            except Exception as ef:
                print(f"  ⚠️ Lỗi đọc frame: {ef}")
                
        try:
            page.screenshot(path="rongbay_debug_frame.png")
            print("\n📸 Đã chụp rongbay_debug_frame.png")
        except Exception as e:
            print("⚠️ Lỗi screenshot:", e)
            
        browser.close()

if __name__ == "__main__":
    test()
