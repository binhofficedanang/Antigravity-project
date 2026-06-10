import time
import os
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print("1. Navigating to https://rongbay.com/...")
        page.goto("https://rongbay.com/", wait_until="domcontentloaded")
        time.sleep(3)
        
        print("2. Clicking login link...")
        page.evaluate("document.querySelector('a.hm_link_login').click()")
        
        # Wait for URL to change to vietid
        print("3. Waiting for URL to become vietid...")
        for i in range(15):
            url = page.url
            print(f"   Current URL: {url}")
            if "vietid" in url:
                break
            time.sleep(1)
            
        print("4. Wait for page load...")
        time.sleep(5)
        
        # Save HTML
        html = page.content()
        with open("rb_debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved rb_debug_page.html")
        
        # Log input tags
        inputs = page.locator("input").all()
        print(f"Found {len(inputs)} inputs:")
        for idx, inp in enumerate(inputs):
            try:
                name = inp.get_attribute("name")
                id_attr = inp.get_attribute("id")
                type_attr = inp.get_attribute("type")
                placeholder = inp.get_attribute("placeholder")
                class_attr = inp.get_attribute("class")
                visible = inp.is_visible()
                print(f"  [{idx}] Input: name={name}, id={id_attr}, type={type_attr}, placeholder={placeholder}, class={class_attr}, visible={visible}")
            except Exception as e:
                print(f"  [{idx}] Error reading attributes: {e}")
                
        # Log button tags
        buttons = page.locator("button, input[type='submit']").all()
        print(f"Found {len(buttons)} buttons:")
        for idx, btn in enumerate(buttons):
            try:
                text = btn.inner_text().strip() or btn.get_attribute("value") or ""
                id_attr = btn.get_attribute("id")
                class_attr = btn.get_attribute("class")
                visible = btn.is_visible()
                print(f"  [{idx}] Button: text='{text}', id={id_attr}, class={class_attr}, visible={visible}")
            except Exception as e:
                print(f"  [{idx}] Error reading button attributes: {e}")

        # Screenshot
        page.screenshot(path="rb_debug_final.png")
        print("Saved rb_debug_final.png")

        browser.close()

if __name__ == "__main__":
    main()
