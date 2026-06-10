#!/usr/bin/env python3
import time
from playwright.sync_api import sync_playwright

PHONE = "0935723727"
PASSWORD = "Binh1995@"

def main():
    with sync_playwright() as p:
        print("Launching visible browser...")
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        try:
            print("Going to muaban.net...")
            page.goto("https://muaban.net/", timeout=60000)
            time.sleep(5)
            
            print("Opening login modal...")
            page.locator("text=Đăng nhập").first.click()
            time.sleep(3)
            
            print("Filling credentials...")
            page.fill("input#phone", PHONE)
            page.fill("input#password", PASSWORD)
            
            print("Please solve Cloudflare Turnstile if needed...")
            time.sleep(10)
            
            print("Navigating to https://muaban.net/dang-tin ...")
            page.goto("https://muaban.net/dang-tin", timeout=60000)
            time.sleep(5)
            
            # Click "Bất động sản"
            print("Clicking 'Bất động sản'...")
            page.locator("text=Bất động sản").first.click()
            time.sleep(3)
            page.screenshot(path="scratch/muaban_step1_bds.png")
            print("Saved scratch/muaban_step1_bds.png")
            
            # Let's see what sub-categories appear.
            # In Vietnamese, it's usually "Cho thuê" -> "Cho thuê văn phòng, cửa hàng, mặt bằng"
            # Let's print out what text is visible on the screen now
            elements = page.evaluate("""
                () => {
                    const texts = [];
                    document.querySelectorAll('div, li, span, p').forEach(el => {
                        const text = el.innerText ? el.innerText.trim() : '';
                        if (text && text.length < 100 && !texts.includes(text)) {
                            texts.push(text);
                        }
                    });
                    return texts;
                }
            """)
            print("Visible text elements on Step 2:")
            for t in elements[:50]:
                print(f"- {t}")
                
            # Click "Sang nhượng, Cho thuê" or "Cho thuê" if it exists
            # Let's try to click Cho thuê nhà đất
            chothue_btn = page.locator("text=Cho thuê nhà đất, văn phòng, cửa hàng, mặt bằng, đất").first
            if chothue_btn.count() == 0:
                chothue_btn = page.locator("text=Cho thuê nhà đất").first
            if chothue_btn.count() == 0:
                chothue_btn = page.locator("text=Cho thuê").first
                
            if chothue_btn.count() > 0:
                print(f"Clicking: {chothue_btn.inner_text()}")
                chothue_btn.click()
                time.sleep(3)
                page.screenshot(path="scratch/muaban_step2_chothue.png")
                print("Saved scratch/muaban_step2_chothue.png")
                
                # Next sub-category: "Cho thuê văn phòng, mặt bằng" or similar
                vp_btn = page.locator("text=Cho thuê văn phòng, mặt bằng, cửa hàng").first
                if vp_btn.count() == 0:
                    vp_btn = page.locator("text=Cho thuê văn phòng").first
                if vp_btn.count() == 0:
                    vp_btn = page.locator("text=Văn phòng").first
                    
                if vp_btn.count() > 0:
                    print(f"Clicking: {vp_btn.inner_text()}")
                    vp_btn.click()
                    time.sleep(3)
                    page.screenshot(path="scratch/muaban_step3_vp.png")
                    print("Saved scratch/muaban_step3_vp.png")
            
            input("Nhấn ENTER để đóng trình duyệt...")
            
        except Exception as e:
            print(f"Error: {e}")
            
        browser.close()

if __name__ == "__main__":
    main()
