import os
import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Đang truy cập trang đăng nhập...")
        page.goto("https://raovat.net/dang-nhap", wait_until="domcontentloaded")
        time.sleep(1)
        
        page.fill("input[name='useremail']", "binh.officedanang@gmail.com")
        page.fill("input[name='password']", "Binh1995@")
        page.click("button#buttonLogin")
        time.sleep(3)
        print(f"URL sau đăng nhập: {page.url}")
        
        print("Truy cập bước 1...")
        page.goto("https://raovat.net/dang-tin-11-Nha-cua-Dat-dai", wait_until="domcontentloaded")
        time.sleep(2)
        
        with open("raovat_step1.html", "w", encoding="utf-8") as f:
            f.write(page.content())
            
        try:
            page.evaluate("""
                () => {
                    const subDiv = document.querySelector('.sub-cate[onclick*="51"]');
                    if (subDiv) subDiv.click();
                }
            """)
            time.sleep(1)
            page.evaluate("document.getElementById('frmStep1').submit()")
            time.sleep(4)
            
            print(f"Đã sang bước 2. URL: {page.url}")
            
            with open("raovat_step2.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            page.screenshot(path="raovat_step2.png", full_page=True)
            print("Đã lưu HTML và ảnh chụp Bước 2.")
            
        except Exception as e:
            print("Lỗi chuyển bước:", e)
            
        browser.close()

if __name__ == "__main__":
    inspect()
