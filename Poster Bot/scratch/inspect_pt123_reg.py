from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://phongtro123.com/dang-ky", timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path="phongtro123_register_page.png")
            print("Title:", page.title())
            
            inputs = page.locator("input, button").all()
            for inp in inputs:
                tag = inp.evaluate("el => el.tagName.toLowerCase()")
                name = inp.get_attribute("name")
                id_ = inp.get_attribute("id")
                type_ = inp.get_attribute("type")
                placeholder = inp.get_attribute("placeholder")
                print(f"[{tag}] Name: {name}, ID: {id_}, Type: {type_}, Placeholder: {placeholder}")
        except Exception as e:
            print("Error:", e)
        browser.close()

if __name__ == "__main__":
    inspect()
