#!/usr/bin/env python3
import time
from playwright.sync_api import sync_playwright

PHONE = "0935723727"
PASSWORD = "Binh1995@"

def main():
    with sync_playwright() as p:
        print("Launching visible browser...")
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        try:
            print("Going to muaban.net...")
            page.goto("https://muaban.net/", timeout=60000)
            time.sleep(5)
            
            print("Opening login modal by JS...")
            page.evaluate("Array.from(document.querySelectorAll('button, div')).find(e => e.innerText && e.innerText.trim() === 'Đăng nhập').click()")
            time.sleep(3)
            
            print("Filling credentials...")
            page.fill("input#phone", PHONE)
            page.fill("input#password", PASSWORD)
            
            # Click submit
            page.evaluate("Array.from(document.querySelectorAll('button')).find(e => e.innerText && e.innerText.trim() === 'Đăng nhập').click()")
            print("Wait 10s for login and Cloudflare...")
            time.sleep(10)
            
            print("Navigating to dang-tin...")
            page.goto("https://muaban.net/dang-tin", timeout=60000)
            time.sleep(5)
            
            # Click Bất động sản
            print("Clicking Bất động sản...")
            page.evaluate("""() => {
                const els = Array.from(document.querySelectorAll('div, li, span, p'));
                const bds = els.find(e => e.innerText && e.innerText.trim() === 'Bất động sản');
                if (bds) bds.click();
            }""")
            time.sleep(3)
            
            # Click Cho thuê nhà đất
            print("Clicking Cho thuê nhà đất...")
            page.evaluate("""() => {
                const els = Array.from(document.querySelectorAll('div, li, span, p'));
                const ct = els.find(e => e.innerText && e.innerText.includes('Cho thuê nhà đất'));
                if (ct) ct.click();
            }""")
            time.sleep(3)
            
            # Click Cho thuê văn phòng
            print("Clicking Cho thuê văn phòng...")
            page.evaluate("""() => {
                const els = Array.from(document.querySelectorAll('div, li, span, p'));
                const vp = els.find(e => e.innerText && e.innerText.includes('Cho thuê văn phòng'));
                if (vp) vp.click();
            }""")
            time.sleep(5)
            
            # Print form elements
            print("Scanning posting form elements...")
            inputs = page.evaluate("""
                () => {
                    const inpList = [];
                    document.querySelectorAll('input, textarea, select, button').forEach(el => {
                        inpList.push({
                            tagName: el.tagName,
                            type: el.type || '',
                            name: el.name || '',
                            id: el.id || '',
                            placeholder: el.placeholder || '',
                            className: el.className || '',
                            text: el.innerText ? el.innerText.trim() : ''
                        });
                    });
                    return inpList;
                }
            """)
            print(f"Found {len(inputs)} elements on the posting page:")
            for idx, el in enumerate(inputs[:100]):
                name_str = f"name='{el['name']}'" if el['name'] else ""
                id_str = f"id='{el['id']}'" if el['id'] else ""
                placeholder_str = f"placeholder='{el['placeholder']}'" if el['placeholder'] else ""
                text_str = f"text='{el['text'][:30]}'" if el['text'] else ""
                print(f"{idx}: <{el['tagName']} type='{el['type']}' {name_str} {id_str} {placeholder_str} {text_str} class='{el['className'][:40]}'>")
                
            page.screenshot(path="scratch/muaban_post_form_js.png")
            print("Saved scratch/muaban_post_form_js.png")
            
        except Exception as e:
            print(f"Error: {e}")
            
        browser.close()

if __name__ == "__main__":
    main()
