import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://123nhadatviet.com/dang-tin.html")
        time.sleep(3)
        
        # Get select options
        selects = ["loaitin", "loaibds", "tinh", "cachtinh"]
        for sel_id in selects:
            options = page.evaluate(f"""() => {{
                const sel = document.getElementById('{sel_id}');
                if (!sel) return [];
                return Array.from(sel.options).map(o => ({{ value: o.value, text: o.text.trim() }}));
            }}""")
            print(f"Options for {sel_id} (count {len(options)}):")
            for opt in options[:15]:
                print(f"  {opt['value']}: {opt['text']}")
            if len(options) > 15:
                print("  ...")
        
        browser.close()

if __name__ == "__main__":
    inspect()
