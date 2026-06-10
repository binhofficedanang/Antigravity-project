import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("http://nhadatviet247.net/dang-tin.html", timeout=30000)
            time.sleep(3)
            print("Title:", page.title())
            inputs = ["tieude", "noidung", "loaitin", "loaibds", "tinh", "huyen", "diachi", "dientich", "gia", "cachtinh", "captcha"]
            for inp_id in inputs:
                el = page.locator(f"#{inp_id}").first
                is_present = el.count() > 0
                is_vis = el.is_visible() if is_present else False
                print(f"Input #{inp_id}: present={is_present}, visible={is_vis}")
        except Exception as e:
            print("Error:", e)
        browser.close()

if __name__ == "__main__":
    inspect()
