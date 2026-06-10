import os
import time
from playwright.sync_api import sync_playwright

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    session_dir = os.path.join(base_dir, "browser_sessions")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            headless=False,
            channel="chrome" if os.path.exists("/Applications/Google Chrome.app") else None
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        print("Goto phongtro123 post page...")
        page.goto("https://phongtro123.com/quan-ly/dang-tin-moi.html", wait_until="networkidle")
        page.wait_for_timeout(5000)
        
        # We know there are 3 select dropdowns. Let's select Đà Nẵng in the first one.
        # Find the value for Đà Nẵng
        val_dn = page.evaluate("""() => {
            const selects = document.querySelectorAll('select');
            if (selects.length === 0) return null;
            const opt = Array.from(selects[0].options).find(o => o.text.includes('Đà Nẵng'));
            return opt ? opt.value : null;
        }""")
        print(f"Đà Nẵng value: {val_dn}")
        
        if val_dn:
            page.locator("select").first.select_option(val_dn)
            print("Selected Đà Nẵng.")
            page.wait_for_timeout(3000)
            
            # Find and select District value (Hải Châu)
            val_hc = page.evaluate("""() => {
                const selects = document.querySelectorAll('select');
                if (selects.length < 2) return null;
                const opt = Array.from(selects[1].options).find(o => o.text.includes('Hải Châu'));
                return opt ? opt.value : null;
            }""")
            print(f"Hải Châu value: {val_hc}")
            if val_hc:
                page.locator("select").nth(1).select_option(val_hc)
                print("Selected Quận Hải Châu.")
                page.wait_for_timeout(3000)
                
                # Find and select Ward value (Ward other than "Tất cả")
                val_w = page.evaluate("""() => {
                    const selects = document.querySelectorAll('select');
                    if (selects.length < 3) return null;
                    const opt = Array.from(selects[2].options).find(o => !o.text.includes('Tất cả') && o.value);
                    return opt ? opt.value : null;
                }""")
                print(f"Ward value: {val_w}")
                if val_w:
                    page.locator("select").nth(2).select_option(val_w)
                    print("Selected Ward.")
                    page.wait_for_timeout(2000)
        
        # Click "Tiếp tục"
        btn = page.locator("button[type='submit']:has-text('Tiếp tục'), button:has-text('Tiếp tục')").first
        if btn.is_visible():
            print("Clicking 'Tiếp tục'...")
            btn.click()
            page.wait_for_timeout(5000)
            print(f"New URL: {page.url}")
            page.screenshot(path="phongtro123_step2.png")
            
            # Print new form fields
            inputs = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
                    tag: el.tagName,
                    id: el.id,
                    name: el.name,
                    placeholder: el.placeholder || '',
                    type: el.type || ''
                }));
            }""")
            print("Step 2 fields:")
            for inp in inputs:
                print(inp)
        else:
            print("Next button not found!")
            
        browser.close()

if __name__ == "__main__":
    main()
