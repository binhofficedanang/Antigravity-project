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
    
    print("Navigating to nhathue page...")
    bot.page.goto("https://dangtinbatdongsan.vn/qttv/nhathue", wait_until="domcontentloaded")
    time.sleep(3)
    
    print("Clicking 'Thêm' button...")
    bot.page.click("#btnThem")
    time.sleep(3)
    
    bot.safe_screenshot("dangtin_nhathue_popup.png")
    
    # Check if elements are now visible/enabled
    inputs = bot.page.locator("input, textarea, select").all()
    print(f"Total elements after clicking Thêm: {len(inputs)}")
    for idx, inp in enumerate(inputs):
        try:
            if inp.is_visible():
                tag = inp.evaluate("el => el.tagName")
                id_val = inp.get_attribute("id")
                name_val = inp.get_attribute("name")
                type_val = inp.get_attribute("type")
                val = inp.evaluate("el => el.value")
                print(f"  Visible Element {idx}: tag={tag}, id={id_val}, name={name_val}, type={type_val}, value={val}")
        except Exception as e:
            pass
            
finally:
    bot.stop()
