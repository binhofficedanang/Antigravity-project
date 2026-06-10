import time
from playwright.sync_api import sync_playwright
import json

def test():
    with open('config.json', 'r') as f:
        config = json.load(f)
    email = config['raovat.net']['username']
    password = config['raovat.net']['password']

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print("Đăng nhập...")
        page.goto("https://raovat.net/dang-nhap")
        try:
            page.fill("input[name='useremail']", email)
            page.fill("input[name='password']", password)
            page.click("button#buttonLogin")
            time.sleep(4)
        except Exception as e:
            print("Lỗi đăng nhập:", e)
            browser.close()
            return
            
        print("Vào trang chọn danh mục...")
        page.goto("https://raovat.net/dang-tin-11-Nha-cua-Dat-dai")
        time.sleep(3)
        
        # In ra các form
        forms = page.locator("form").all()
        print(f"Tìm thấy {len(forms)} forms:")
        for idx, form in enumerate(forms):
            print(f"  Form {idx}: id={form.get_attribute('id')}, action={form.get_attribute('action')}")
            inputs = form.locator("input").all()
            for inp in inputs:
                print(f"    - Input: name={inp.get_attribute('name')}, type={inp.get_attribute('type')}, value={inp.get_attribute('value')}")
        
        # In ra các phần tử onclick 51 hoặc chứa sub-cate
        subcates = page.locator(".sub-cate, [onclick*='51'], [href*='51']").all()
        print(f"Tìm thấy {len(subcates)} sub-category elements:")
        for sc in subcates:
            print(f"  - Element: tag={sc.evaluate('el => el.tagName')}, class={sc.get_attribute('class')}, text={sc.inner_text().strip()}, onclick={sc.get_attribute('onclick')}")
            
        browser.close()

if __name__ == "__main__":
    test()
