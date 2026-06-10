import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

bot = WebAutomation(headless=False)
try:
    bot.start()
    
    # Listen to dialogs
    def handle_dialog(dialog):
        print(f"Dialog appeared: type={dialog.type}, message='{dialog.message}'")
        dialog.accept()
    bot.page.on("dialog", handle_dialog)
    
    bot.page.goto("https://dangtinbatdongsan.vn/qttv", wait_until="domcontentloaded")
    time.sleep(2)
    bot.page.fill("#txtTenDangNhap", "binhofficedanang")
    bot.page.fill("#txtMatKhau", "Binh1995@")
    bot.safe_screenshot("dangtin_before_click.png")
    
    print("Clicking submit...")
    bot.page.click("#btnDangNhap")
    time.sleep(5)
    bot.safe_screenshot("dangtin_after_click.png")
    print(f"Final URL: {bot.page.url}")
    print(f"Page header text (h1/h2): {[el.text_content().strip() for el in bot.page.locator('h1, h2').all()]}")
    
finally:
    bot.stop()
