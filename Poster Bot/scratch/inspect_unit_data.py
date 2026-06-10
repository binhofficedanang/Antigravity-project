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
    
    bot.page.goto("https://dangtinbatdongsan.vn/qttv/nhathue", wait_until="domcontentloaded")
    time.sleep(3)
    bot.page.click("#btnThem")
    time.sleep(2)
    
    data = bot.page.evaluate("""() => {
        try {
            return $('#cboDonViGiaBan').combobox('getData');
        } catch(e) {
            return e.message;
        }
    }""")
    print("cboDonViGiaBan Data:", data)
    
finally:
    bot.stop()
