import time
from playwright.sync_api import sync_playwright

def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Đang truy cập rongbay.com...")
        try:
            page.goto("https://rongbay.com/", wait_until="commit", timeout=15000)
            time.sleep(10) # Chờ 10 giây để nội dung hiện ra
        except Exception as e:
            print(f"Trang tải chậm: {e}")
            time.sleep(5)
        page.screenshot(path="rongbay_home.png", full_page=True)
        html = page.content()
        with open("rongbay_home.html", "w") as f:
            f.write(html)
        browser.close()

if __name__ == "__main__":
    scrape()
