import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_automation import WebAutomation

def main():
    bot = WebAutomation(headless=True)
    bot.start()
    
    username = "binhofficedanang"
    password = "Binh1995@"
    
    try:
        # Log in
        login_ok = bot.login_123nhadatviet(username, password)
        print(f"Login success: {login_ok}")
        
        # Go to posting page
        bot.page.goto("http://123nhadatviet.com/dang-tin.html", wait_until="domcontentloaded")
        time.sleep(3)
        print(f"Current URL: {bot.page.url}")
        
        # Capture full-page screenshot
        bot.page.screenshot(path="logged_in_dang_tin_full.png", full_page=True)
        print("Captured full page screenshot: logged_in_dang_tin_full.png")
        
        # Print all visible input fields and their labels
        inputs = bot.page.locator("input, select, textarea").all()
        print(f"Total inputs: {len(inputs)}")
        for idx, inp in enumerate(inputs):
            try:
                name = inp.get_attribute("name")
                id_attr = inp.get_attribute("id")
                tag = inp.evaluate("e => e.tagName")
                is_vis = inp.is_visible()
                val = inp.input_value() if tag in ["INPUT", "TEXTAREA"] else ""
                print(f"  [{idx}] {tag}: id='{id_attr}', name='{name}', visible={is_vis}, val='{val}'")
            except Exception as e:
                pass
                
    except Exception as e:
        print("Error:", e)
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
