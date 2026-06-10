import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://123nhadatviet.com/dang-tin.html")
        time.sleep(3)
        
        # Check for iframes or script references to editors
        has_cke = page.evaluate("() => typeof CKEDITOR !== 'undefined'")
        has_tinymce = page.evaluate("() => typeof tinyMCE !== 'undefined'")
        
        # Find all iframes
        iframes = page.locator("iframe").all()
        print(f"CKEDITOR present: {has_cke}")
        print(f"TinyMCE present: {has_tinymce}")
        print(f"Total iframes: {len(iframes)}")
        for idx, iframe in enumerate(iframes):
            try:
                name = iframe.get_attribute("name")
                id_attr = iframe.get_attribute("id")
                src = iframe.get_attribute("src")
                print(f"  [{idx}] name='{name}', id='{id_attr}', src='{src}'")
            except Exception as e:
                print(f"  [{idx}] Error: {e}")
                
        browser.close()

if __name__ == "__main__":
    inspect()
