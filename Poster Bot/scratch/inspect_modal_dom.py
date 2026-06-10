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
        
        # Find all elements that are visible and have text related to login
        elements = page.locator("a, div, span, input").all()
        print(f"Total elements: {len(elements)}")
        for idx, el in enumerate(elements):
            try:
                if el.is_visible():
                    text = el.inner_text().strip()
                    id_attr = el.get_attribute("id")
                    class_attr = el.get_attribute("class")
                    onclick = el.get_attribute("onclick")
                    
                    if "đăng nhập" in text.lower() or "login" in text.lower() or (onclick and "login" in onclick.lower()):
                        print(f"  [{idx}] Tag={el.evaluate('e => e.tagName')}, text='{text}', id='{id_attr}', class='{class_attr}', onclick='{onclick}'")
            except Exception:
                pass
                
        browser.close()

if __name__ == "__main__":
    inspect()
