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
            const el = $('#cboDonViGiaBan');
            if (el.hasClass('combotree-f')) {
                return { type: 'combotree', roots: el.combotree('tree').tree('getRoots').map(n => ({id: n.id, text: n.text})) };
            } else if (el.hasClass('combobox-f')) {
                return { type: 'combobox', data: el.combobox('getData').map(n => ({id: n.id, text: n.text})) };
            } else {
                // Try direct select or check classes
                return { type: 'unknown', classes: el.attr('class') };
            }
        } catch(e) {
            return e.message;
        }
    }""")
    print("cboDonViGiaBan Info:", data)
    
finally:
    bot.stop()
