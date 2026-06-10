import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_geo():
    # Load config
    config_path = "../config.json" if os.path.exists("../config.json") else "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    account = config.get("thuviennhadat.vn", {})
    username = account.get("username", "0935723727")
    password = account.get("password", "Binh1995@")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("1. Đăng nhập vào thuviennhadat.vn...")
        page.goto("https://thuviennhadat.vn/Users/Login?returnUrl=%2Fdang-tin", wait_until="domcontentloaded")
        time.sleep(2)
        
        page.fill("input#phone-mail-login-view", username)
        page.fill("input#password-login-view", password)
        page.click("button#button-submit-login-view")
        try:
            page.wait_for_url("**/dang-tin**", timeout=15000)
            time.sleep(3)
        except Exception as e:
            print(f"Lỗi chuyển trang sau đăng nhập: {e}")
            page.screenshot(path="scratch/login_fail.png")
            raise e
            
        print(f"URL hiện tại: {page.url}")
        
        # Điền Nhu cầu
        print("2. Chọn Nhu cầu (Cho thuê)...")
        try:
            page.click(".tag._post-transaction-type._rent", timeout=10000)
            time.sleep(1)
        except Exception as e:
            print(f"Lỗi click chọn Nhu cầu: {e}")
            page.screenshot(path="scratch/rent_click_fail.png")
            raise e

        # Mở modal địa chỉ
        print("3. Mở modal địa chỉ...")
        try:
            page.click("input[name='PostFullAddress']", timeout=10000)
        except Exception as e:
            page.screenshot(path="scratch/address_click_fail.png")
            raise e
        time.sleep(2)
        
        # Chọn thành phố Đà Nẵng
        print("3. Chọn thành phố Đà Nẵng...")
        page.click("div.ui.search.dropdown._input-city")
        time.sleep(1)
        page.fill("div.ui.search.dropdown._input-city input.search", "Đà Nẵng")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(2)
        
        # Lấy danh sách các Quận/Huyện khả dụng
        print("4. Lấy danh sách Quận/Huyện...")
        districts = page.evaluate("""
            () => {
                const items = document.querySelectorAll('div.ui.search.dropdown._input-dictrict div.menu div.item');
                return Array.from(items).map(item => ({
                    text: item.innerText.strip ? item.innerText.strip() : item.innerText,
                    value: item.getAttribute('data-value')
                }));
            }
        """)
        
        print(f"Tìm thấy {len(districts)} Quận/Huyện:")
        for d in districts:
            print(f" - {d['text']} (value: {d['value']})")
            
        # Với mỗi quận/huyện, chọn thử để xem danh sách Phường/Xã khả dụng
        geo_map = {}
        for d in districts:
            dist_text = d['text']
            dist_value = d['value']
            
            # Chọn quận này
            print(f"Chọn Quận/Huyện: {dist_text} ...")
            page.click("div.ui.search.dropdown._input-dictrict")
            time.sleep(1)
            # Click vào item tương ứng
            page.click(f"div.ui.search.dropdown._input-dictrict div.menu div.item[data-value='{dist_value}']")
            time.sleep(2)
            
            # Đọc danh sách Phường/Xã
            wards = page.evaluate("""
                () => {
                    const items = document.querySelectorAll('div.ui.search.dropdown._input-ward div.menu div.item');
                    return Array.from(items).map(item => item.innerText.trim());
                }
            """)
            print(f"   => Các Phường/Xã khả dụng ({len(wards)}): {wards[:5]} ...")
            geo_map[dist_text] = wards
            
        print("\n=== HOÀN TẤT BẢN ĐỒ ĐỊA CHÍ ===")
        print(json.dumps(geo_map, ensure_ascii=False, indent=4))
        
        browser.close()

if __name__ == "__main__":
    inspect_geo()
