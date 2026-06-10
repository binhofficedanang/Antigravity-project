import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://123nhadatviet.com/dang-tin.html")
        time.sleep(3)
        
        # Select city (3 = Đà Nẵng)
        print("Selecting city: 3...")
        page.select_option("#tinh", "3")
        time.sleep(2)
        
        # Select district (e.g. Hải Châu)
        huyen_options = page.evaluate("""() => {
            const sel = document.getElementById('huyen');
            if (!sel) return [];
            return Array.from(sel.options).map(o => ({ value: o.value, text: o.text.trim() }));
        }""")
        print("Huyen options:", huyen_options)
        
        # Let's find 'Hải Châu' value
        huyen_val = ""
        for opt in huyen_options:
            if "hải châu" in opt["text"].lower():
                huyen_val = opt["value"]
                break
        
        if huyen_val:
            print(f"Selecting huyen: {huyen_val} ({opt['text']})...")
            page.select_option("#huyen", huyen_val)
            time.sleep(2)
            
            # Now let's inspect '#phuong' and '#duong'
            for sel_id in ["phuong", "duong"]:
                options = page.evaluate(f"""() => {{
                    const sel = document.getElementById('{sel_id}');
                    if (!sel) return [];
                    return Array.from(sel.options).map(o => ({{ value: o.value, text: o.text.trim() }}));
                }}""")
                print(f"Options for {sel_id} (count {len(options)}):")
                for opt in options[:10]:
                    print(f"  {opt['value']}: {opt['text']}")
                if len(options) > 10:
                    print("  ...")
        else:
            print("Hải Châu not found in district options.")
            
        browser.close()

if __name__ == '__main__':
    inspect()
