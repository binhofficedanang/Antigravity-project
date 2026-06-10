from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://muabandanang.vn/dang-nhap", timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path="muabandanang_login_page.png")
            print("Title:", page.title())
            
            inputs = page.locator("input").all()
            for inp in inputs:
                name = inp.get_attribute("name")
                id_ = inp.get_attribute("id")
                type_ = inp.get_attribute("type")
                placeholder = inp.get_attribute("placeholder")
                print(f"Input - Name: {name}, ID: {id_}, Type: {type_}, Placeholder: {placeholder}")
                
            buttons = page.locator("button").all()
            for btn in buttons:
                print(f"Button - Text: {btn.inner_text()}, Type: {btn.get_attribute('type')}")
        except Exception as e:
            print("Error:", e)
        browser.close()

if __name__ == "__main__":
    inspect()
