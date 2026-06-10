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
    
    # Print outer HTML of cboTTP's parent
    parent_html = bot.page.evaluate("""() => {
        const el = document.getElementById('cboTTP');
        return el ? el.parentElement.outerHTML : 'Not found cboTTP';
    }""")
    print("cboTTP Parent HTML:")
    print(parent_html[:2000]) # Print first 2000 chars
    
    # Check if there is any combo panel
    panels = bot.page.evaluate("""() => {
        return Array.from(document.querySelectorAll('.combo-panel, .panel')).map(el => ({
            className: el.className,
            id: el.id,
            text: el.innerText.substring(0, 100)
        }));
    }""")
    print("Combo Panels on page:", panels)
    
finally:
    bot.stop()
