import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

bot = WebAutomation(headless=False)
try:
    bot.start()
    bot.register_dangtinbatdongsan("binhofficedanang", "Binh1995@", "binh.officedanang@gmail.com", "0935723727")
    bot.safe_screenshot("dangtin_after_register_attempt.png")
    time.sleep(2)
finally:
    bot.stop()
