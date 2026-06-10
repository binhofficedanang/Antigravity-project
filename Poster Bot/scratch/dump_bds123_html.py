import os
import sys
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from web_automation import WebAutomation

def main():
    bot = WebAutomation(headless=True)
    try:
        bot.start()
        print("Navigating to https://bds123.vn/dang-nhap.html...")
        bot.page.goto("https://bds123.vn/dang-nhap.html", wait_until="domcontentloaded")
        time.sleep(5)
        
        url = bot.page.url
        title = bot.page.title()
        print(f"URL: {url}")
        print(f"Title: {title}")
        
        # Check if cloudflare challenge is present
        content = bot.page.content()
        print(f"Length of HTML content: {len(content)}")
        
        if "cf-challenge" in content or "cloudflare" in content.lower() or "checking your browser" in content.lower():
            print("Detected Cloudflare page!")
        else:
            print("Not Cloudflare. Let's print the first 1000 chars of HTML:")
            print(content[:1000])
            
            # Print all input names/ids
            inputs = bot.page.locator("input, select, textarea, button").all()
            print(f"Total input/select/textarea/button elements: {len(inputs)}")
            for idx, inp in enumerate(inputs):
                tag = inp.evaluate("el => el.tagName")
                name = inp.get_attribute("name") or ""
                id_attr = inp.get_attribute("id") or ""
                type_attr = inp.get_attribute("type") or ""
                placeholder = inp.get_attribute("placeholder") or ""
                is_visible = inp.is_visible()
                print(f"  [{idx}] <{tag}> name='{name}' id='{id_attr}' type='{type_attr}' placeholder='{placeholder}' visible={is_visible}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
