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
    
    # Run Javascript to get the data of the comboboxes
    ttp_data = bot.page.evaluate("""() => {
        try {
            return $('#cboTTP').combobox('getData');
        } catch(e) {
            return e.message;
        }
    }""")
    print("cboTTP Data:", ttp_data)
    
    # Let's set TTP to Da Nang (if we find its code) to load Xa
    # Usually Da Nang code is '48' or similar. Let's try to set it to '48' or search the ttp_data first
    da_nang_code = None
    if isinstance(ttp_data, list):
        for item in ttp_data:
            text = item.get('text', '').lower()
            if 'đà nẵng' in text or 'da nang' in text:
                da_nang_code = item.get('id')
                print(f"Found Đà Nẵng code: {da_nang_code}")
                break
                
    if da_nang_code:
        bot.page.evaluate(f"$('#cboTTP').combobox('setValue', '{da_nang_code}')")
        time.sleep(2) # wait for Xa to load
        
        xa_data = bot.page.evaluate("""() => {
            try {
                return $('#cboXa').combobox('getData');
            } catch(e) {
                return e.message;
            }
        }""")
        print("cboXa Data:", xa_data)
        
    nhom_data = bot.page.evaluate("""() => {
        try {
            return $('#cboNhomNhaThue').combobox('getData');
        } catch(e) {
            return e.message;
        }
    }""")
    print("cboNhomNhaThue Data:", nhom_data)
    
finally:
    bot.stop()
