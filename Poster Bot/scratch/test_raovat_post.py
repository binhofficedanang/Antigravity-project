import time
from playwright.sync_api import sync_playwright
import json

def test():
    with open('config.json', 'r') as f:
        config = json.load(f)
    email = config['raovat.net']['email']
    password = config['raovat.net']['password']

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        page.on("console", lambda msg: print("CONSOLE:", msg.text))
        
        # 1. Login
        print("Đăng nhập raovat.net...")
        page.goto("https://raovat.net/dang-nhap")
        time.sleep(2)
        try:
            page.fill("input[name='useremail']", email)
            page.fill("input[name='password']", password)
            page.click("button#buttonLogin")
            time.sleep(4)
            print("Đăng nhập thành công, URL:", page.url)
        except Exception as e:
            print("Lỗi đăng nhập:", e)
            browser.close()
            return
            
        # 2. Go to Step 1
        print("Mở trang chọn danh mục...")
        page.goto("https://raovat.net/dang-tin-11-Nha-cua-Dat-dai", wait_until="domcontentloaded")
        time.sleep(3)
        
        # Click subcategory via JS (to bypass loading modal overlay)
        print("Click chọn subcategory via JS...")
        page.evaluate("() => { const el = document.querySelector('.sub-cate[onclick*=\"51\"]'); if(el) el.click(); }")
        
        # Wait for the "Tiếp tục" button to appear (it gets class 'hidden' removed or is not hidden)
        print("Đợi nút Tiếp tục xuất hiện (không còn hidden)...")
        try:
            btn_ready = False
            for _ in range(10):
                is_hidden = page.evaluate("() => { const btn = document.querySelector('#btnNextStep button'); return btn ? btn.classList.contains('hidden') : true; }")
                if not is_hidden:
                    btn_ready = True
                    break
                time.sleep(1)
            
            if btn_ready:
                print("Nút Tiếp tục đã sẵn sàng! Thực hiện click Tiếp tục via JS...")
                page.evaluate("() => { document.querySelector('#btnNextStep button').click(); }")
            else:
                print("Nút Tiếp tục vẫn hidden. Force click Tiếp tục via JS anyway...")
                page.evaluate("""
                    () => {
                        const btn = document.querySelector('#btnNextStep button');
                        if (btn) {
                            btn.classList.remove('hidden');
                            btn.click();
                        }
                    }
                """)
        except Exception as e:
            print("Lỗi click Tiếp tục:", e)
            
        # Wait for Step 2 page
        print("Đợi chuyển sang Step 2...")
        time.sleep(5)
        print("URL hiện tại:", page.url)
        page.screenshot(path="raovat_step1_final_click.png")
        
        # Check if sitetitle is present
        sitetitle = page.locator("input[name='sitetitle']")
        if sitetitle.count() > 0:
            print("🎉 THÀNH CÔNG! Đã chuyển sang Step 2. Tìm thấy input[name='sitetitle']")
        else:
            print("❌ Thất bại. Vẫn ở Step 1 hoặc trang khác.")
            
        browser.close()

if __name__ == "__main__":
    test()
