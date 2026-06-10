#!/usr/bin/env python3
"""
Script debug từng bước cho muaban.net:
1. Đăng nhập
2. Vào trang đăng tin
3. Chọn danh mục Bất động sản -> Cho thuê -> Văn phòng
4. Chụp screenshot và dump HTML sau mỗi bước
5. Scan toàn bộ input fields
"""
import time
import json
from playwright.sync_api import sync_playwright

def main():
    print("=== Debug muaban.net step by step ===")
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    account = config.get('muaban_account', {})
    email = account.get('email', '')
    password = account.get('password', '')
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        # === BƯỚC 1: Đăng nhập ===
        print("\n[BƯỚC 1] Đăng nhập...")
        page.goto("https://muaban.net/dang-nhap", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        page.screenshot(path="scratch/muaban_step1_login.png")
        
        try:
            page.fill("input[type='email'], input[name='email'], input[placeholder*='Email']", email, timeout=5000)
            page.fill("input[type='password']", password, timeout=5000)
            page.click("button[type='submit'], button:has-text('Đăng nhập')", timeout=5000)
            time.sleep(4)
            print(f"  - Đăng nhập xong. URL: {page.url}")
        except Exception as e:
            print(f"  - Lỗi đăng nhập: {e}")
        
        page.screenshot(path="scratch/muaban_step1b_after_login.png")
        
        # === BƯỚC 2: Vào trang đăng tin ===
        print("\n[BƯỚC 2] Vào trang đăng tin...")
        page.goto("https://muaban.net/dang-tin", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        page.screenshot(path="scratch/muaban_step2_dangtin.png")
        print(f"  - URL: {page.url}")
        print(f"  - Title: {page.title()}")
        
        # Kiểm tra có modal không
        modal = page.locator("[class*='modal'], [role='dialog'], [class*='Modal']")
        print(f"  - Modal count: {modal.count()}")
        
        # Scan tất cả elements có thể click
        clickable = page.locator("text=Bất động sản")
        print(f"  - 'Bất động sản' elements: {clickable.count()}")
        for i in range(clickable.count()):
            el = clickable.nth(i)
            print(f"    [{i}] visible={el.is_visible()}, tag={el.evaluate('el => el.tagName')}, text='{el.inner_text()[:50]}'")
        
        # === BƯỚC 3: Click Bất động sản ===
        print("\n[BƯỚC 3] Click vào 'Bất động sản'...")
        try:
            # Thử nhiều cách
            attempts = [
                lambda: page.locator("text=Bất động sản").first.click(timeout=5000),
                lambda: page.get_by_text("Bất động sản", exact=True).first.click(timeout=5000),
                lambda: page.locator("li:has-text('Bất động sản')").first.click(timeout=5000),
                lambda: page.locator("a:has-text('Bất động sản')").first.click(timeout=5000),
                lambda: page.locator("div:has-text('Bất động sản')").first.click(timeout=5000),
            ]
            
            clicked = False
            for i, attempt in enumerate(attempts):
                try:
                    attempt()
                    print(f"  - Thành công với cách {i+1}")
                    clicked = True
                    break
                except Exception as e:
                    print(f"  - Cách {i+1} thất bại: {e}")
            
            if not clicked:
                print("  - TẤT CẢ đều thất bại! Cần kiểm tra HTML.")
                
        except Exception as e:
            print(f"  - Lỗi tổng: {e}")
        
        time.sleep(2)
        page.screenshot(path="scratch/muaban_step3_after_bat_dong_san.png")
        
        # === BƯỚC 4: Click Cho thuê ===
        print("\n[BƯỚC 4] Click 'Cho thuê'...")
        cho_thue = page.locator("text=Cho thuê")
        print(f"  - 'Cho thuê' elements: {cho_thue.count()}")
        try:
            cho_thue.first.click(timeout=5000)
            print("  - Đã click Cho thuê")
        except Exception as e:
            print(f"  - Lỗi: {e}")
        
        time.sleep(2)
        page.screenshot(path="scratch/muaban_step4_after_cho_thue.png")
        
        # === BƯỚC 5: Click Văn phòng ===
        print("\n[BƯỚC 5] Click 'Văn phòng'...")
        van_phong_options = ["text=Văn phòng, mặt bằng", "text=Văn phòng"]
        for opt in van_phong_options:
            el = page.locator(opt)
            if el.count() > 0:
                try:
                    el.first.click(timeout=5000)
                    print(f"  - Đã click: {opt}")
                    break
                except Exception as e:
                    print(f"  - Lỗi: {e}")
        
        time.sleep(3)
        page.screenshot(path="scratch/muaban_step5_after_van_phong.png")
        print(f"  - URL sau khi chọn danh mục: {page.url}")
        
        # === BƯỚC 6: Scan toàn bộ form fields ===
        print("\n[BƯỚC 6] Scan form fields...")
        inputs = page.locator("input, textarea, select")
        count = inputs.count()
        print(f"  - Tổng số input/textarea/select: {count}")
        
        for i in range(min(count, 30)):
            el = inputs.nth(i)
            try:
                tag = el.evaluate('el => el.tagName')
                itype = el.evaluate('el => el.type || ""')
                name = el.evaluate('el => el.name || ""')
                placeholder = el.evaluate('el => el.placeholder || ""')
                cls = el.evaluate('el => el.className || ""')[:50]
                visible = el.is_visible()
                print(f"  [{i}] {tag}[type={itype}] name='{name}' placeholder='{placeholder}' visible={visible}")
            except:
                pass
        
        # Dump HTML của main content
        try:
            main_html = page.locator("main, #__next, [class*='content'], form").first.inner_html()
            with open("scratch/muaban_form_html.html", "w", encoding="utf-8") as f:
                f.write(main_html[:50000])
            print("\n  - Đã lưu HTML vào scratch/muaban_form_html.html")
        except Exception as e:
            print(f"  - Không lưu được HTML: {e}")
            # Dump toàn bộ page
            try:
                page.content()
                with open("scratch/muaban_form_html.html", "w", encoding="utf-8") as f:
                    f.write(page.content()[:50000])
            except: pass
        
        print("\n=== XONG! Giữ trình duyệt mở 20 giây để bạn quan sát ===")
        time.sleep(20)
        browser.close()

if __name__ == "__main__":
    main()
