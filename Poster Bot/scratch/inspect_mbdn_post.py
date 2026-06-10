import os
import time
from playwright.sync_api import sync_playwright

def inspect():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    session_dir = os.path.join(base_dir, "browser_sessions")
    
    username = "binhofficedanang"
    password = "Binh1995@"
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            headless=True,
            args=["--start-maximized"]
        )
        page = browser.new_page()
        try:
            # 1. Login
            print("Logging in to muabandanang.vn...")
            page.goto("https://muabandanang.vn/dang-nhap", timeout=30000)
            page.wait_for_timeout(3000)
            
            if page.locator("#user_login").is_visible():
                page.fill("#user_login", username)
                page.fill("#user_pass", password)
                page.click("#wp-submit")
                page.wait_for_timeout(5000)
                print("Login submitted. Current URL:", page.url)
            
            # 2. Go to dang-tin
            print("Navigating to dang-tin...")
            page.goto("https://muabandanang.vn/dang-tin", timeout=30000)
            page.wait_for_timeout(5000)
            page.screenshot(path="muabandanang_post_form.png")
            print("Post form page title:", page.title())
            print("Current URL:", page.url)
            
            # Print inputs
            inputs = page.locator("input, select, textarea").all()
            for inp in inputs:
                tag = inp.evaluate("el => el.tagName.toLowerCase()")
                name = inp.get_attribute("name")
                id_ = inp.get_attribute("id")
                type_ = inp.get_attribute("type")
                placeholder = inp.get_attribute("placeholder")
                print(f"[{tag}] Name: {name}, ID: {id_}, Type: {type_}, Placeholder: {placeholder}")
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    inspect()
