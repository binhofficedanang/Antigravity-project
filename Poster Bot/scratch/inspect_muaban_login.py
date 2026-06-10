#!/usr/bin/env python3
import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})
        
        try:
            print("Navigating to muaban.net login page...")
            page.goto("https://muaban.net/dang-nhap", timeout=30000)
            time.sleep(5)
            page.screenshot(path="scratch/muaban_login_page.png")
            print("Saved muaban_login_page.png")
            with open("scratch/muaban_login_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("Saved muaban_login_page.html")
            
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="scratch/muaban_login_error.png")
            
        browser.close()

if __name__ == "__main__":
    main()
