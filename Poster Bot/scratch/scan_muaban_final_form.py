#!/usr/bin/env python3
import time
import json
from playwright.sync_api import sync_playwright

def main():
    print("Testing muaban.net category selection to reach final form...")
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    acc = config.get("muaban.net", {})
    username = acc.get("username")
    password = acc.get("password")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            page.goto("https://muaban.net/")
            time.sleep(3)
            
            # Login
            login_btn = page.locator("text=Đăng nhập").first
            if login_btn.count() > 0:
                login_btn.click()
                time.sleep(2)
                page.fill("input[name='phone'], input[type='tel']", username)
                page.fill("input[name='password'], input[type='password']", password)
                submit_btn = page.locator("button.iyHKgc, button:has-text('Đăng nhập')").last
                submit_btn.click()
                time.sleep(5)
            
            # Go to post page
            page.goto("https://muaban.net/dang-tin")
            time.sleep(5)
            
            # Click categories
            print("Clicking categories...")
            page.locator("text=Bất động sản").first.click(timeout=5000)
            time.sleep(2)
            page.locator("text=Cho thuê").first.click(timeout=5000)
            time.sleep(2)
            vp = page.locator("text=Văn phòng, mặt bằng").first
            if vp.count() == 0:
                vp = page.locator("text=Văn phòng").first
            vp.click(timeout=5000)
            time.sleep(5)
            
            # Scan form
            print("Scanning inputs on the final form...")
            inputs = page.evaluate("""
                () => {
                    const inpList = [];
                    document.querySelectorAll('input, textarea, select').forEach(el => {
                        inpList.push({
                            tagName: el.tagName,
                            type: el.type || '',
                            name: el.name || '',
                            id: el.id || '',
                            placeholder: el.placeholder || '',
                            className: el.className || ''
                        });
                    });
                    return inpList;
                }
            """)
            print(f"Found {len(inputs)} form elements:")
            for idx, el in enumerate(inputs):
                print(f"{idx}: <{el['tagName']} type='{el['type']}' name='{el['name']}' id='{el['id']}' placeholder='{el['placeholder']}' class='{el['className']}'>")
                
            page.screenshot(path="scratch/muaban_final_form.png")
            print("Saved scratch/muaban_final_form.png")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
