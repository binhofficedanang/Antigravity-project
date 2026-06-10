import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

bot = WebAutomation(headless=False)
try:
    bot.start()
    bot.login_dangtinbatdongsan("binhofficedanang", "Binh1995@")
    time.sleep(3)
    
    # Take a screenshot to inspect the logged in page state
    bot.safe_screenshot("dangtin_logged_in_home.png")
    print(f"Current URL: {bot.page.url}")
    
    # Print all links on the page
    links = bot.page.locator("a").all()
    print(f"Total links on page: {len(links)}")
    for idx, link in enumerate(links):
        try:
            text = link.text_content().strip()
            href = link.get_attribute("href")
            # Filter links containing "tin" or "dang" or look like a posting page
            if "tin" in text.lower() or "đăng" in text.lower() or (href and ("dang" in href or "tin" in href or "qttv" in href)):
                print(f"  Link {idx}: text='{text}', href='{href}'")
        except:
            pass
            
finally:
    bot.stop()
