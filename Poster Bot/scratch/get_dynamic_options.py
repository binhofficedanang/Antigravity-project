import os
import time
from playwright.sync_api import sync_playwright

def inspect():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    session_dir = os.path.join(base_dir, "browser_sessions")
    
    username = "binhofficedanang"
    password = "Binh1995@"
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            headless=True
        )
        page = browser.new_page()
        try:
            print("Logging in...")
            page.goto("https://muabandanang.vn/dang-nhap", timeout=30000)
            page.wait_for_timeout(3000)
            if page.locator("#user_login").is_visible():
                page.fill("#user_login", username)
                page.fill("#user_pass", password)
                page.click("#wp-submit")
                page.wait_for_timeout(5000)
                
            print("Going to dang-tin page...")
            page.goto("https://muabandanang.vn/dang-tin", timeout=30000)
            page.wait_for_timeout(3000)
            
            # Select realty-rent
            print("Selecting type-realty = realty-rent...")
            page.select_option("select[name='type-realty']", "realty-rent")
            page.wait_for_timeout(3000)  # Wait for term-type options to load
            
            # Get term-type options
            options_term = page.evaluate("""() => {
                const el = document.querySelector('select[name="term-type"]');
                if (!el) return [];
                return Array.from(el.options).map(o => ({text: o.text, value: o.value}));
            }""")
            print("\nDynamic options for term-type after choosing Cho thuê:")
            for opt in options_term:
                print(f"  {opt['text']} -> {opt['value']}")
                
            # Select city = 2341 (Đà Nẵng)
            print("\nSelecting city = 2341...")
            page.select_option("select[name='city']", "2341")
            page.wait_for_timeout(3000)  # Wait for ward options to load
            
            # Get ward options
            options_ward = page.evaluate("""() => {
                const el = document.querySelector('select[name="ward"]');
                if (!el) return [];
                return Array.from(el.options).map(o => ({text: o.text, value: o.value}));
            }""")
            print("\nDynamic options for ward after choosing Đà Nẵng (first 30):")
            for opt in options_ward[:30]:
                print(f"  {opt['text']} -> {opt['value']}")
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    inspect()
