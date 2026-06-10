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
        
        print("Navigating to muaban.net...")
        try:
            page.goto("https://muaban.net/", timeout=30000, wait_until="networkidle")
            print("Successfully loaded muaban.net")
            page.screenshot(path="scratch/muaban_home.png")
            print("Saved muaban_home.png")
            
            # Let's search for "đăng tin" or price / post ad options.
            content = page.content()
            with open("scratch/muaban_home.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("Saved muaban_home.html")
            
            # Check register page
            print("Navigating to register page...")
            page.goto("https://muaban.net/dang-ky", timeout=30000)
            time.sleep(3)
            page.screenshot(path="scratch/muaban_register.png")
            print("Saved muaban_register.png")
            with open("scratch/muaban_register.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("Saved muaban_register.html")
            
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="scratch/muaban_error.png")
            
        browser.close()

if __name__ == "__main__":
    main()
