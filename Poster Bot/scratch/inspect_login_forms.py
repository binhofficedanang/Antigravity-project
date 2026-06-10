import time
from playwright.sync_api import sync_playwright
import os

sites = [
    {"name": "123nhadatviet.com", "url": "http://123nhadatviet.com"},
    {"name": "vatgia.com", "url": "https://www.vatgia.com/user/login"},
    {"name": "nhadatviet247.net", "url": "http://nhadatviet247.net"},
    {"name": "batdongsangiatot.com.vn", "url": "https://batdongsangiatot.com.vn/member-login.html"},
    {"name": "dangtinbatdongsan.vn", "url": "https://dangtinbatdongsan.vn"},
    {"name": "chonhadat24h.com", "url": "https://chonhadat24h.com/dang-nhap"}
]

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for s in sites:
            print(f"\n======================================")
            print(f"SITE: {s['name']} -> {s['url']}")
            print(f"======================================")
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()
            
            try:
                page.goto(s['url'], wait_until="domcontentloaded", timeout=30000)
                time.sleep(3)
                
                # If the URL is the main page and requires clicking login
                if s['name'] in ["123nhadatviet.com", "nhadatviet247.net", "dangtinbatdongsan.vn"]:
                    print("  - Attempting to click login button/link...")
                    login_btn = None
                    # Search for elements containing "Đăng nhập"
                    for sel in ["a:has-text('Đăng nhập')", "span:has-text('Đăng nhập')", "div:has-text('Đăng nhập')", "text=Đăng nhập"]:
                        try:
                            loc = page.locator(sel)
                            if loc.count() > 0:
                                # click the first visible
                                for i in range(loc.count()):
                                    el = loc.nth(i)
                                    if el.is_visible():
                                        el.click()
                                        print(f"    ✓ Clicked element matching: {sel}")
                                        login_btn = el
                                        break
                            if login_btn:
                                break
                        except Exception:
                            continue
                    time.sleep(3)
                
                # Check current url and title
                print(f"  URL hiện tại: {page.url}")
                print(f"  Tiêu đề: {page.title()}")
                
                # Dump forms and inputs
                inputs = page.locator("input").all()
                print(f"  Inputs found: {len(inputs)}")
                for idx, inp in enumerate(inputs[:10]):
                    try:
                        name = inp.get_attribute("name")
                        id_attr = inp.get_attribute("id")
                        type_attr = inp.get_attribute("type")
                        placeholder = inp.get_attribute("placeholder")
                        is_vis = inp.is_visible()
                        print(f"    [{idx}] name='{name}', id='{id_attr}', type='{type_attr}', placeholder='{placeholder}', visible={is_vis}")
                    except Exception as e_inp:
                        print(f"    [{idx}] Error reading input: {e_inp}")
                        
                # Take screenshot for visual check
                filename = f"inspect_{s['name'].replace('.', '_')}.png"
                page.screenshot(path=filename)
                print(f"  📸 Screenshot saved: {filename}")
                
            except Exception as e:
                print(f"  ⚠️ Error inspecting site {s['name']}: {e}")
                
            context.close()
        browser.close()

if __name__ == "__main__":
    inspect()
