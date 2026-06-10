import asyncio
import os
import sys
import time
from playwright.async_api import async_playwright

USERNAME = "binhofficedanang"
PASSWORD = "Binh1995@"

async def test_nhadat_vn_details():
    print("--- STARTING NHADAT.VN DETAILED POST INSPECTION ---")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        # Login via HTTPS
        print("Navigating to https://raovat.nhadat.vn/...")
        await page.goto("https://raovat.nhadat.vn/", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)
        
        # Fill login
        await page.fill("#navbar_username", USERNAME)
        try:
            await page.click("#navbar_password_hint")
            await page.wait_for_timeout(500)
        except:
            pass
        await page.fill("#navbar_password", PASSWORD)
        await page.click("input[type='submit'][value='Đăng nhập']")
        await page.wait_for_timeout(5000)
        
        # Go to posting page
        print("Navigating to posting page...")
        await page.goto("https://raovat.nhadat.vn/dangtin.html", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        
        # Parse radio buttons and their texts
        print("\nParsing category options:")
        categories = await page.evaluate("""() => {
            const list = [];
            const inputs = document.querySelectorAll("input[name='f']");
            for (let inp of inputs) {
                let text = "";
                // Try to get text node next to the input
                let nextNode = inp.nextSibling;
                while (nextNode) {
                    if (nextNode.nodeType === 3) { // Text node
                        text += nextNode.textContent.trim();
                    } else if (nextNode.nodeType === 1) { // Element node
                        text += nextNode.innerText.trim();
                    }
                    nextNode = nextNode.nextSibling;
                }
                if (!text && inp.parentElement) {
                    text = inp.parentElement.innerText.trim();
                }
                list.push({ value: inp.value, text: text.trim(), visible: inp.offsetHeight > 0 });
            }
            return list;
        }""")
        
        for cat in categories:
            if cat['visible'] or cat['text']:
                print(f"  Value: {cat['value']} -> Text: '{cat['text']}' (visible={cat['visible']})")
                
        # Find the form and submit button
        submit_btn = await page.locator("form[action*='dangtin.html'] input[type='submit'], form input[type='submit']:not([value='Đăng nhập'])").all()
        print(f"\nFound submit buttons: {len(submit_btn)}")
        for idx, btn in enumerate(submit_btn):
            val = await btn.get_attribute("value") or ""
            print(f"  [{idx}] value='{val}'")
            
        # Let's try to find a category related to Cho thuê/Văn phòng
        # Look at options
        target_val = None
        for cat in categories:
            if not cat['visible']:
                continue
            t = cat['text'].lower()
            if "cho thuê" in t and "văn phòng" in t:
                target_val = cat['value']
                print(f"Match found for Cho thuê văn phòng: value={target_val} ('{cat['text']}')")
                break
                
        if not target_val:
            for cat in categories:
                if not cat['visible']:
                    continue
                t = cat['text'].lower()
                if "cho thuê" in t or "văn phòng" in t:
                    print(f"Partial match: value={cat['value']} ('{cat['text']}')")
                    target_val = cat['value'] # Fallback to any partial match
                    
        if target_val:
            print(f"\nSelecting category value={target_val} and submitting...")
            # Click/check the radio button
            await page.locator(f"input[name='f'][value='{target_val}']").click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path="nhadat_category_selected.png")
            
            # Click the submit button
            # Usually the submit button is the one with value "Tiếp tục" or similar
            if len(submit_btn) > 0:
                await submit_btn[0].click()
            else:
                await page.evaluate("() => { document.querySelector('form').submit(); }")
                
            await page.wait_for_timeout(5000)
            print(f"Post Page Step 2 URL: {page.url}")
            await page.screenshot(path="nhadat_post_step2.png")
            
            # Dump inputs on Step 2
            print("\nDumping form elements on Step 2:")
            inputs = await page.locator("input, select, textarea, button").all()
            print(f"Total elements on Step 2: {len(inputs)}")
            for idx, inp in enumerate(inputs):
                tag = await inp.evaluate("el => el.tagName")
                name = await inp.get_attribute("name") or ""
                id_attr = await inp.get_attribute("id") or ""
                type_attr = await inp.get_attribute("type") or ""
                value_attr = await inp.get_attribute("value") or ""
                placeholder = await inp.get_attribute("placeholder") or ""
                is_visible = await inp.is_visible()
                if name or id_attr or is_visible:
                    print(f"  [{idx}] <{tag}> name='{name}' id='{id_attr}' type='{type_attr}' value='{value_attr}' placeholder='{placeholder}' visible={is_visible}")
                    
            # Let's inspect the Select elements for locations
            selects = await page.locator("select").all()
            for idx, sel in enumerate(selects):
                name = await sel.get_attribute("name") or ""
                id_attr = await sel.get_attribute("id") or ""
                options = await sel.locator("option").all()
                print(f"\nSelect [{idx}] name='{name}' id='{id_attr}' options count: {len(options)}")
                for opt in options[:10]:
                    val = await opt.get_attribute("value") or ""
                    text = await opt.inner_text()
                    print(f"  Option val='{val}' text='{text.strip()}'")
                if len(options) > 10:
                    print(f"  ... and {len(options) - 10} more options")
        else:
            print("No matching category value found!")

        await browser.close()
        print("--- INSPECTION COMPLETED ---")

if __name__ == "__main__":
    asyncio.run(test_nhadat_vn_details())
