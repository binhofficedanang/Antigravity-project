#!/usr/bin/env python3
import time
import json
from playwright.sync_api import sync_playwright

def main():
    print("Dumping HTML of muaban dang tin page...")
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
            
            page.goto("https://muaban.net/dang-tin")
            time.sleep(5)
            
            # Dump the initial HTML
            html = page.content()
            with open("scratch/muaban_dangtin.html", "w") as f:
                f.write(html)
            print("Saved scratch/muaban_dangtin.html")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
