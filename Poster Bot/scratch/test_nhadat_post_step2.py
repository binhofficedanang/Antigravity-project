import asyncio
from playwright.async_api import async_playwright

USERNAME = "binhofficedanang"
PASSWORD = "Binh1995@"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        # 1. Login on HTTP homepage
        print("Navigating to http://raovat.nhadat.vn/...")
        await page.goto("http://raovat.nhadat.vn/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        print("Logging in...")
        await page.fill("#navbar_username", USERNAME)
        try:
            await page.click("#navbar_password_hint")
            await page.wait_for_timeout(500)
        except:
            pass
        await page.fill("#navbar_password", PASSWORD)
        await page.click("input[type='submit'][value='Đăng nhập']")
        await page.wait_for_timeout(6000)
        
        # Verify if logged in by checking page content/title
        print(f"Logged in? URL: {page.url}, Title: {await page.title()}")
        
        # 2. Go to posting page
        print("Navigating to posting page: http://raovat.nhadat.vn/dangtin.html...")
        await page.goto("http://raovat.nhadat.vn/dangtin.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        print(f"Posting page URL: {page.url}")
        
        # 3. Check radio button 59 and click next
        # Let's see if we have form on the page
        print("Selecting category value 59...")
        await page.locator("input[name='f'][value='59']").click()
        await page.wait_for_timeout(1000)
        await page.screenshot(path="nhadat_step1_ready.png")
        
        # The submit button on step 1: let's find it. It might be inside a form.
        # Let's find any submit button or use form submit
        print("Submitting step 1 form...")
        submit_btn = page.locator("form input[type='submit']:not([value='Đăng nhập'])").first
        if await submit_btn.count() > 0:
            await submit_btn.click()
        else:
            await page.evaluate("() => { document.querySelector('form').submit(); }")
            
        await page.wait_for_timeout(6000)
        print(f"After submit step 1. URL: {page.url}")
        await page.screenshot(path="nhadat_step2_loaded.png")
        
        # Dump all inputs on step 2
        inputs = await page.locator("input, select, textarea, button").all()
        print(f"Total elements on step 2: {len(inputs)}")
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
                
        # Dump select dropdowns
        selects = await page.locator("select").all()
        for idx, sel in enumerate(selects):
            name = await sel.get_attribute("name") or ""
            id_attr = await sel.get_attribute("id") or ""
            options = await sel.locator("option").all()
            print(f"\nSelect [{idx}] name='{name}' id='{id_attr}' options count: {len(options)}")
            for opt in options[:15]:
                val = await opt.get_attribute("value") or ""
                text = await opt.inner_text()
                print(f"  Option val='{val}' text='{text.strip()}'")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
