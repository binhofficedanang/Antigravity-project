import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://123nhadatviet.com")
        time.sleep(3)
        
        # Find href for "Đăng tin miễn phí"
        href = page.evaluate("""() => {
            const el = Array.from(document.querySelectorAll('a')).find(a => a.innerText.includes('Đăng tin'));
            return el ? el.href : null;
        }""")
        print("Href for Đăng tin:", href)
        
        if href:
            page.goto(href)
            time.sleep(3)
            print("URL hiện tại:", page.url)
            print("Tiêu đề:", page.title())
            
            # Print all input names and IDs
            inputs = page.locator("input, select, textarea").all()
            print(f"Inputs/Selects/Textareas found: {len(inputs)}")
            for idx, inp in enumerate(inputs[:30]):
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
