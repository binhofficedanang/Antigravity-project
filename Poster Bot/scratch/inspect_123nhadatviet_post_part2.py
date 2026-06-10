import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://123nhadatviet.com/dang-tin.html")
        time.sleep(3)
        
        # Print all input names, ids, and tags from index 30 to 63
        inputs = page.locator("input, select, textarea, button").all()
        print(f"Total: {len(inputs)}")
        for idx in range(30, len(inputs)):
            inp = inputs[idx]
            try:
                tag = inp.evaluate("e => e.tagName")
                name = inp.get_attribute("name")
                id_attr = inp.get_attribute("id")
                type_attr = inp.get_attribute("type")
                placeholder = inp.get_attribute("placeholder")
                is_vis = inp.is_visible()
                print(f"  [{idx}] {tag}: name='{name}', id='{id_attr}', type='{type_attr}', placeholder='{placeholder}', visible={is_vis}")
            except Exception as e:
                print(f"  [{idx}] Error: {e}")
                
        browser.close()

if __name__ == "__main__":
    inspect()
