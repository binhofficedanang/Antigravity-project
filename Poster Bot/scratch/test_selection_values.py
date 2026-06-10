import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_automation import WebAutomation

def main():
    bot = WebAutomation(headless=True)
    bot.start()
    
    address_lower = "đường 2/9, p. hòa cường bắc, hải châu, đà nẵng"
    
    try:
        bot.page.goto("https://123nhadatviet.com/dang-tin.html")
        time.sleep(3)
        
        # Select tinh
        bot.page.select_option("#tinh", "3")
        time.sleep(2)
        
        # Select huyen
        bot.page.evaluate("() => { const el = document.getElementById('huyen'); el.value = '584'; el.dispatchEvent(new Event('change')); }")
        time.sleep(2)
        
        # Ward mapping logic
        ward_options = bot.page.evaluate("""() => {
            const sel = document.getElementById('phuong');
            if (!sel) return [];
            return Array.from(sel.options).map(o => ({ value: o.value, text: o.text.toLowerCase() }));
        }""")
        
        valid_wards = [opt for opt in ward_options if opt["value"] != "" and "----" not in opt["text"]]
        valid_wards.sort(key=lambda x: len(x["text"]), reverse=True)
        
        phuong_val = ""
        for opt in valid_wards:
            clean_opt_text = opt["text"].replace("phường", "").replace("phuong", "").strip()
            if clean_opt_text in address_lower:
                phuong_val = opt["value"]
                break
        if not phuong_val and len(ward_options) > 1:
            phuong_val = ward_options[1]["value"]
            
        print("Computed phuong_val:", phuong_val)
        
        # Street mapping logic
        street_options = bot.page.evaluate("""() => {
            const sel = document.getElementById('duong');
            if (!sel) return [];
            return Array.from(sel.options).map(o => ({ value: o.value, text: o.text.toLowerCase() }));
        }""")
        duong_val = ""
        for opt in street_options:
            if opt["value"] == "" or "----" in opt["text"]:
                continue
            clean_opt_text = opt["text"].replace("đường", "").replace("duong", "").replace("đ. ", "").replace("đ.", "").strip()
            if clean_opt_text in address_lower:
                duong_val = opt["value"]
                break
        if not duong_val and len(street_options) > 1:
            duong_val = street_options[1]["value"]
            
        print("Computed duong_val:", duong_val)
        
    except Exception as e:
        print("Error:", e)
    finally:
        bot.stop()

if __name__ == '__main__':
    main()
