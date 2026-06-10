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
            print("Logging in first...")
            page.goto("https://muabandanang.vn/dang-nhap", timeout=30000)
            page.wait_for_timeout(3000)
            
            if page.locator("#user_login").is_visible():
                page.fill("#user_login", username)
                page.fill("#user_pass", password)
                page.click("#wp-submit")
                page.wait_for_timeout(5000)
                
            print("Going to dang-tin page...")
            page.goto("https://muabandanang.vn/dang-tin", timeout=30000)
            page.wait_for_timeout(5000)
            
            selects = ["type-realty", "term-type", "city", "ward"]
            for sel_name in selects:
                print(f"\nOptions for select name='{sel_name}':")
                options = page.evaluate(f"""(selName) => {{
                    const el = document.querySelector(`select[name="${{selName}}"]`);
                    if (!el) return [];
                    return Array.from(el.options).map(o => ({{text: o.text, value: o.value}}));
                }}""", sel_name)
                for opt in options[:20]:  # Limit print to first 20 options
                    print(f"  {opt['text']} -> {opt['value']}")
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    inspect()
