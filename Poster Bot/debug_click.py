from playwright.sync_api import sync_playwright
import time

def debug_rongbay_click():
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
                
            print("Navigating to dang_tin_rao_vat.html...")
            page.goto("https://rongbay.com/dang_tin_rao_vat.html", wait_until="domcontentloaded")
            time.sleep(3)
            
            # Click the main category: Thuê, Cho thuê nhà (lang="272")
            print("Hovering over main category...")
            page.hover("li.choose_cat[lang='272']")
            time.sleep(2)
            
            # Click the sub category: Cao ốc văn phòng (lang="296" lang2="636")
            # First hover Cho thuê văn phòng (if needed) or just click the sub category
            print("Clicking sub category Cao ốc văn phòng...")
            page.click("a[lang='296'][lang2='636']")
            time.sleep(5)
            
            with open("rongbay_form_after_click.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("Saved form HTML after click")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    debug_rongbay_click()
