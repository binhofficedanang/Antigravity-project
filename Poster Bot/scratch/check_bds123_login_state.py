import os
import sys
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from web_automation import WebAutomation

def main():
    bot = WebAutomation(headless=True)
    try:
        bot.start()
        print("Navigating to https://bds123.vn/...")
        bot.page.goto("https://bds123.vn/", wait_until="domcontentloaded")
        time.sleep(3)
        
        url = bot.page.url
        title = bot.page.title()
        print(f"Current URL: {url}")
        print(f"Current Title: {title}")
        
        # Check login state using dropdown-toggle or other selectors
        body_text = bot.page.content()
        
        # Let's search for user profile/name
        is_logged_in = False
        user_text = ""
        try:
            bot.page.wait_for_selector(".dropdown-toggle", timeout=5000)
            user_text = bot.page.locator(".dropdown-toggle").first.inner_text().strip()
            print(f"Dropdown toggle text: '{user_text}'")
            if user_text and "tài khoản" not in user_text.lower() and "đăng nhập" not in user_text.lower():
                is_logged_in = True
        except Exception as e:
            print(f"Error checking dropdown-toggle: {e}")
            
        try:
            # Let's search for logout or personal page indicators
            if "thoát" in body_text.lower() or "đăng xuất" in body_text.lower():
                is_logged_in = True
                print("Found logout/exit link in body HTML")
        except Exception as e:
            pass
            
        print(f"LOGGED IN STATE: {is_logged_in}")
        bot.safe_screenshot("bds123_check_login.png")
        
        # Go to dang-tin.html
        print("Navigating to https://bds123.vn/dang-tin.html...")
        bot.page.goto("https://bds123.vn/dang-tin.html", wait_until="domcontentloaded")
        time.sleep(3)
        print(f"Dang tin URL: {bot.page.url}")
        bot.safe_screenshot("bds123_dang_tin_page.png")
        
        # Check if the posting form is visible
        if bot.page.locator("textarea[name='post_title']").count() > 0 or bot.page.locator("input[name='title']").count() > 0:
            print("Posting form is visible and ready!")
        else:
            print("Posting form is NOT visible.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
