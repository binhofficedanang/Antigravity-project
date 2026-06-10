import asyncio
import os
from playwright.async_api import async_playwright

USERNAME = "binhofficedanang"
PASSWORD = "Binh1995@"

async def check_nhadat():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        # Go to HTTP homepage
        print("Navigating to http://raovat.nhadat.vn/...")
        await page.goto("http://raovat.nhadat.vn/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        # Fill login on HTTP page
        await page.fill("#navbar_username", USERNAME)
        try:
            await page.click("#navbar_password_hint")
            await page.wait_for_timeout(500)
        except:
            pass
        await page.fill("#navbar_password", PASSWORD)
        await page.click("input[type='submit'][value='Đăng nhập']")
        await page.wait_for_timeout(5000)
        
        print(f"URL after HTTP login click: {page.url}")
        
        # Check if we are logged in on this page
        body_text = await page.inner_text("body")
        print(f"Is 'Đăng nhập' still in body? {'Đăng nhập' in body_text}")
        print(f"Is 'Thoát' or 'Đăng xuất' or username in body? {'thoát' in body_text.lower() or 'đăng xuất' in body_text.lower() or USERNAME in body_text.lower()}")
        
        # Print navbar HTML segment
        navbar_html = await page.evaluate("() => { const el = document.querySelector('#navbar') || document.querySelector('.header') || document.body; return el ? el.innerHTML : ''; }")
        print("\nNavbar/Header HTML segment:")
        print(navbar_html[:800])
        
        # Go to posting page (both HTTP and HTTPS)
        for url in ["http://raovat.nhadat.vn/dangtin.html", "https://raovat.nhadat.vn/dangtin.html"]:
            print(f"\n--- Testing posting page URL: {url} ---")
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
            # Print form action
            form_action = await page.evaluate("() => { const form = document.querySelector('form'); return form ? form.action : 'No form found'; }")
            print(f"Form action URL: {form_action}")
            
            # Print page title and body login indicators
            title = await page.title()
            body = await page.inner_text("body")
            print(f"Page Title: {title}")
            print(f"Is logged in indicators on this page? {'đăng xuất' in body.lower() or 'thoát' in body.lower() or USERNAME in body.lower()}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_nhadat())
