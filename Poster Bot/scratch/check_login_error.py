import asyncio
from playwright.async_api import async_playwright

USERNAME = "binhofficedanang"
PASSWORD = "Binh1995@"

async def check_login_error():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        print("Navigating to http://raovat.nhadat.vn/...")
        await page.goto("http://raovat.nhadat.vn/", wait_until="domcontentloaded")
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
        
        print(f"URL after login redirect: {page.url}")
        print(f"Page title: {await page.title()}")
        
        # Print main body content or search for error messages
        body_text = await page.inner_text("body")
        print("\n--- Page Body Text Segment ---")
        lines = body_text.split("\n")
        # Print first 40 non-empty lines
        printed = 0
        for line in lines:
            line_str = line.strip()
            if line_str:
                print(line_str)
                printed += 1
                if printed >= 40:
                    break
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_login_error())
