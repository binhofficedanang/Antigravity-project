import time
from playwright.sync_api import sync_playwright

def scrape_vietid():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Mở trang VietID login trực tiếp...")
        page.goto("https://go.vietid.net/oauth/rb/login", wait_until="domcontentloaded")
        time.sleep(3)
        
        try:
            page.screenshot(path="vietid_login.png", timeout=5000)
            print("Đã chụp vietid_login.png")
        except Exception as e:
            print("Lỗi screenshot:", e)
            
        print("HTML Content:")
        html = page.content()
        with open("vietid_login.html", "w") as f:
            f.write(html)
        
        # In ra các ô input có sẵn
        inputs = page.locator("input").all()
        print(f"Tìm thấy {len(inputs)} input tags:")
        for inp in inputs:
            name = inp.get_attribute("name")
            id_attr = inp.get_attribute("id")
            type_attr = inp.get_attribute("type")
            placeholder = inp.get_attribute("placeholder")
            print(f"  - Input: name={name}, id={id_attr}, type={type_attr}, placeholder={placeholder}")
            
        # In ra các button
        buttons = page.locator("button, input[type='submit']").all()
        print(f"Tìm thấy {len(buttons)} buttons:")
        for btn in buttons:
            name = btn.get_attribute("name")
            id_attr = btn.get_attribute("id")
            text = btn.inner_text().strip() or btn.get_attribute("value")
            print(f"  - Button: name={name}, id={id_attr}, text/value={text}")
            
        browser.close()

if __name__ == "__main__":
    scrape_vietid()
