import os
import sys
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from web_automation import WebAutomation

def main():
    bot = WebAutomation(headless=True)
    try:
        bot.start()
        print("Navigating to https://bds123.vn/dang-tin.html...")
        bot.page.goto("https://bds123.vn/dang-tin.html", wait_until="domcontentloaded")
        time.sleep(3)
        
        print(f"Current URL: {bot.page.url}")
        bot.safe_screenshot("bds123_post_fields_loaded.png")
        
        # Dump all inputs, selects, textareas
        inputs = bot.page.locator("input, select, textarea, button").all()
        print(f"Total elements: {len(inputs)}")
        for idx, inp in enumerate(inputs):
            tag = inp.evaluate("el => el.tagName")
            name = inp.get_attribute("name") or ""
            id_attr = inp.get_attribute("id") or ""
            type_attr = inp.get_attribute("type") or ""
            placeholder = inp.get_attribute("placeholder") or ""
            is_visible = inp.is_visible()
            
            # Print if it has a name, id, or is a select/textarea
            if name or id_attr or tag in ["SELECT", "TEXTAREA"]:
                print(f"  [{idx}] <{tag}> name='{name}' id='{id_attr}' type='{type_attr}' placeholder='{placeholder}' visible={is_visible}")
                
        # Let's inspect the Select elements in detail
        selects = bot.page.locator("select").all()
        for idx, sel in enumerate(selects):
            name = sel.get_attribute("name") or ""
            id_attr = sel.get_attribute("id") or ""
            options = sel.locator("option").all()
            print(f"\nSelect [{idx}] name='{name}' id='{id_attr}' options count: {len(options)}")
            for opt in options[:10]:
                val = opt.get_attribute("value") or ""
                text = opt.inner_text()
                print(f"  Option val='{val}' text='{text.strip()}'")
            if len(options) > 10:
                print(f"  ... and {len(options) - 10} more options")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
