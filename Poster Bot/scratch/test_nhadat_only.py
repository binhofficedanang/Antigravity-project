import asyncio
import os
import sys
import time
from playwright.async_api import async_playwright

USERNAME = "binhofficedanang"
PASSWORD = "Binh1995@"

async def test_nhadat_vn():
    print("--- STARTING NHADAT.VN INSPECTION ---")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        # Go to homepage
        print("Navigating to http://raovat.nhadat.vn/...")
        await page.goto("http://raovat.nhadat.vn/", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        
        # Fill login
        print("Filling login credentials...")
        await page.fill("#navbar_username", USERNAME)
        try:
            await page.click("#navbar_password_hint")
            await page.wait_for_timeout(500)
        except Exception as e:
            print(f"Could not click password hint: {e}")
            
        await page.fill("#navbar_password", PASSWORD)
        await page.screenshot(path="nhadat_login_filled.png")
        
        # Click login button
        print("Clicking login button...")
        await page.click("input[type='submit'][value='Đăng nhập']")
        await page.wait_for_timeout(6000)
        
        print(f"URL after login: {page.url}")
        print(f"Page Title: {await page.title()}")
        await page.screenshot(path="nhadat_after_login.png")
        
        # Navigate to posting page
        print("Navigating to posting page: https://raovat.nhadat.vn/dangtin.html...")
        await page.goto("https://raovat.nhadat.vn/dangtin.html", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)
        
        print(f"Post Page URL: {page.url}")
        await page.screenshot(path="nhadat_post_page.png")
        
        # Dump inputs
        print("\nDumping form elements on posting page:")
        inputs = await page.locator("input, select, textarea, button").all()
        print(f"Total input/select/textarea/button elements: {len(inputs)}")
        for idx, inp in enumerate(inputs):
            tag = await inp.evaluate("el => el.tagName")
            name = await inp.get_attribute("name") or ""
            id_attr = await inp.get_attribute("id") or ""
            type_attr = await inp.get_attribute("type") or ""
            value_attr = await inp.get_attribute("value") or ""
            placeholder = await inp.get_attribute("placeholder") or ""
            is_visible = await inp.is_visible()
            
            # Print if visible or has a name
            if name or id_attr or is_visible:
                print(f"  [{idx}] <{tag}> name='{name}' id='{id_attr}' type='{type_attr}' value='{value_attr}' placeholder='{placeholder}' visible={is_visible}")
                
        # Also print select options if there are dropdowns for category/location
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
            if len(options) > 15:
                print(f"  ... and {len(options) - 15} more options")

        await browser.close()
        print("--- INSPECTION COMPLETED ---")

if __name__ == "__main__":
    asyncio.run(test_nhadat_vn())
