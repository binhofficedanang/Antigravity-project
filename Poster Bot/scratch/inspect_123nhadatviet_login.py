import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://123nhadatviet.com")
        time.sleep(3)
        
        # Click login to open modal
        page.click("a:has-text('Đăng nhập')")
        time.sleep(2)
        
        # Print buttons inside the page
        buttons = page.locator("button, input[type='submit'], a.btn, input[type='button']").all()
        print(f"Buttons found: {len(buttons)}")
        for idx, btn in enumerate(buttons):
            try:
                name = btn.get_attribute("name")
                id_attr = btn.get_attribute("id")
                class_attr = btn.get_attribute("class")
                text = btn.inner_text().strip() or btn.get_attribute("value")
                is_vis = btn.is_visible()
                print(f"  [{idx}] text='{text}', id='{id_attr}', name='{name}', class='{class_attr}', visible={is_vis}")
            except Exception as e:
                print(f"  [{idx}] Error: {e}")
                
        browser.close()

if __name__ == "__main__":
    inspect()
