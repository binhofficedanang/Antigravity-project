#!/usr/bin/env python3
import time
from playwright.sync_api import sync_playwright

PHONE = "0935723727"
PASSWORD = "Binh1995@"

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
            print("Navigating to muaban.net...")
            page.goto("https://muaban.net/", timeout=30000)
            time.sleep(5)
            
            print("Opening login modal...")
            page.locator("text=Đăng nhập").first.click()
            time.sleep(3)
            
            print("Filling credentials...")
            page.fill("input#phone", PHONE)
            page.fill("input#password", PASSWORD)
            
            print("Submitting login...")
            # Click the second 'Đăng nhập' button (the one inside the modal)
            # Let's target the button that is inside the modal or contains iyHKgc class
            login_btn = page.locator("button.iyHKgc, button:has-text('Đăng nhập')").last
            login_btn.click()
            time.sleep(5)
            
            print(f"URL after login submit: {page.url}")
            page.screenshot(path="scratch/muaban_login_result.png")
            print("Saved muaban_login_result.png")
            
            # Let's check if we are successfully logged in
            # We can check if there's any logout button or avatar
            # Now let's try to navigate to post page
            print("Navigating to post page...")
            page.goto("https://muaban.net/dang-tin", timeout=30000)
            time.sleep(5)
            print(f"Post page URL: {page.url}")
            page.screenshot(path="scratch/muaban_post_page.png")
            print("Saved muaban_post_page.png")
            with open("scratch/muaban_post_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("Saved muaban_post_page.html")
            
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="scratch/muaban_post_error.png")
            
        browser.close()

if __name__ == "__main__":
    main()
