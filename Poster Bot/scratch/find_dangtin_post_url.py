import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

bot = WebAutomation(headless=False)
try:
    bot.start()
    bot.login_dangtinbatdongsan("binhofficedanang", "Binh1995@")
    time.sleep(2)
    
    # Locate all 'Đăng tin' buttons/links
    links = bot.page.locator("a:has-text('Đăng tin'), a:has-text('ĐĂNG TIN'), a[href*='dangtin'], a[href*='dang-tin']")
    print(f"Posting links found: {links.count()}")
    for i in range(links.count()):
        print(f"  Link {i}: text='{links.nth(i).text_content().strip()}', href='{links.nth(i).get_attribute('href')}'")
        
finally:
    bot.stop()
