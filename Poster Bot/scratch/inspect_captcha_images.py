import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

bot = WebAutomation(headless=False)
try:
    bot.start()
    
    # 1. DiaOcAnPhu captcha image
    print("\n--- DiaOcAnPhu Captcha Image ---")
    try:
        bot.page.goto("http://diaocanphu.com/dang-ky.html", wait_until="domcontentloaded")
        time.sleep(2)
        images = bot.page.locator("img").all()
        for idx, img in enumerate(images):
            src = img.get_attribute("src") or ""
            id_val = img.get_attribute("id") or ""
            class_val = img.get_attribute("class") or ""
            if "captcha" in src.lower() or "captcha" in id_val.lower() or "captcha" in class_val.lower() or "code" in src.lower():
                print(f"  Img {idx}: src='{src}', id='{id_val}', class='{class_val}'")
    except Exception as e:
        print(f"Error checking DiaOcAnPhu: {e}")
        
    # 2. DatViet24h captcha image
    print("\n--- DatViet24h Captcha Image ---")
    try:
        bot.page.goto("https://datviet24h.com.vn/dang-ky.html", wait_until="domcontentloaded")
        time.sleep(2)
        images = bot.page.locator("img").all()
        for idx, img in enumerate(images):
            src = img.get_attribute("src") or ""
            id_val = img.get_attribute("id") or ""
            class_val = img.get_attribute("class") or ""
            if "captcha" in src.lower() or "captcha" in id_val.lower() or "captcha" in class_val.lower():
                print(f"  Img {idx}: src='{src}', id='{id_val}', class='{class_val}'")
    except Exception as e:
        print(f"Error checking DatViet24h: {e}")
        
finally:
    bot.stop()
