import os
import time
from playwright.sync_api import sync_playwright

def test_raovatdanang():
    print("=== Auto-register raovatdanang.vn ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://raovatdanang.vn/wp-login.php?action=register", timeout=30000)
            page.wait_for_timeout(3000)
            content = page.content()
            page.screenshot(path="raovatdanang_register_page.png")
            print("Page title:", page.title())
            
            # Check inputs
            inputs = page.locator("input").all()
            for inp in inputs:
                name = inp.get_attribute("name")
                id_ = inp.get_attribute("id")
                type_ = inp.get_attribute("type")
                print(f"Input - Name: {name}, ID: {id_}, Type: {type_}")
                
            # If standard WordPress registration is disabled, it usually says "Registration is closed" or redirects.
            if "registration is closed" in content.lower() or "đăng ký thành viên hiện đã đóng" in content.lower():
                print("WP registration is disabled on raovatdanang.vn.")
            else:
                # Fill standard wp registration fields
                # #user_login and #user_email
                if page.locator("#user_login").is_visible():
                    page.fill("#user_login", "binhofficedanang")
                    page.fill("#user_email", "binh.officedanang@gmail.com")
                    page.screenshot(path="raovatdanang_register_filled.png")
                    page.click("#wp-submit")
                    page.wait_for_timeout(5000)
                    page.screenshot(path="raovatdanang_register_result.png")
                    print("Submitted WP registration form on raovatdanang.vn.")
        except Exception as e:
            print("Error raovatdanang.vn:", e)
        browser.close()

def test_chodanang():
    print("\n=== Auto-register chodanang.com ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("http://chodanang.com/", timeout=30000)
            page.wait_for_timeout(3000)
            
            # Look for registration link
            reg_link = page.locator("text=/đăng ký/i").first
            if reg_link.is_visible():
                reg_link.click()
                page.wait_for_timeout(3000)
                print("Registration page URL:", page.url)
                page.screenshot(path="chodanang_register_page.png")
                
                # Check fields
                inputs = page.locator("input").all()
                for inp in inputs:
                    name = inp.get_attribute("name")
                    id_ = inp.get_attribute("id")
                    type_ = inp.get_attribute("type")
                    print(f"Input - Name: {name}, ID: {id_}, Type: {type_}")
            else:
                print("Could not find registration link on chodanang.com homepage.")
        except Exception as e:
            print("Error chodanang.com:", e)
        browser.close()

if __name__ == "__main__":
    test_raovatdanang()
    test_chodanang()
