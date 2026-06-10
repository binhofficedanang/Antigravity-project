from playwright.sync_api import sync_playwright
import time

def debug_rongbay_form():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://rongbay.com/", wait_until="domcontentloaded")
            page.click("text=Đăng nhập", timeout=10000)
            time.sleep(3)
            
            vietid_frame = None
            for frame in page.frames:
                if "vietid.net" in frame.url or "login" in frame.url:
                    vietid_frame = frame
                    break
                    
            if vietid_frame:
                vietid_frame.fill("input[name='account']", "binh.officedanang@gmail.com")
                vietid_frame.click("button.btn-next")
                time.sleep(3)
                vietid_frame.fill("input[type='password']", "Binh1995@")
                vietid_frame.click("button.btn-login")
                print("Clicked login, waiting...")
                time.sleep(5)
                
            print("Navigating to dang_tin_rao_vat.html?catid=296...")
            # Try catid=296
            page.goto("https://rongbay.com/dang_tin_rao_vat.html?catid=296", wait_until="domcontentloaded")
            time.sleep(3)
            
            with open("rongbay_form.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("Saved form HTML for catid=296")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    debug_rongbay_form()
