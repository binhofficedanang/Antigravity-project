import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

bot = WebAutomation(headless=False)
try:
    bot.start()
    
    print("Navigating to http://diaocanphu.com/dang-ky.html ...")
    bot.page.goto("http://diaocanphu.com/dang-ky.html", wait_until="domcontentloaded")
    time.sleep(3)
    
    # Fill form
    bot.page.fill("#username1", "binhofficedanang")
    bot.page.fill("#email", "binh.officedanang@gmail.com")
    bot.page.fill("#password1", "Binh1995@")
    bot.page.fill("#password2", "Binh1995@")
    bot.page.fill("#dienthoai", "0935723727")
    bot.page.fill("#diachi", "Đà Nẵng")
    bot.page.fill("#ten", "Binh Office Da Nang")
    bot.page.fill("#namsinh", "1995")
    
    # Click male
    bot.page.click("#nam")
    
    # Solve captcha using free API
    # Since the ocr.space public key 'helloworld' will extract digits by default in solve_image_captcha_free,
    # let's write a custom captcha fetcher here that keeps letters as well!
    img_element = bot.page.locator("img#vimg").first
    import base64
    import requests
    
    img_bytes = img_element.screenshot(timeout=5000)
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    
    print("Solving alphanumeric captcha via ocr.space free API...")
    url = "https://api.ocr.space/parse/image"
    payload = {
        "apikey": "helloworld",
        "base64Image": f"data:image/png;base64,{img_base64}",
        "language": "eng",
        "isOverlayRequired": False,
        "OCREngine": 2
    }
    r = requests.post(url, data=payload, timeout=15)
    res = r.json()
    parsed_results = res.get("ParsedResults", [])
    captcha_code = ""
    if parsed_results:
        text = parsed_results[0].get("ParsedText", "").strip()
        captcha_code = "".join(c for c in text if c.isalnum())
        print(f"Parsed captcha: '{captcha_code}'")
        
    bot.page.fill("#captcha", captcha_code)
    bot.safe_screenshot("diaocanphu_register_filled.png")
    
    print("Submitting registration...")
    bot.page.click("#login")
    time.sleep(5)
    
    bot.safe_screenshot("diaocanphu_register_result.png")
    print(f"Final URL: {bot.page.url}")
    
finally:
    bot.stop()
