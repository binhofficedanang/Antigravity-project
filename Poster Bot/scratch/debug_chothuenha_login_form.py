"""Tìm đúng form login chothuenha.com.vn"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://chothuenha.com.vn/tai-khoan", timeout=20000)
        await page.wait_for_timeout(2000)
        print(f"URL: {page.url}")
        print(f"Title: {await page.title()}")
        
        # Tất cả inputs
        inputs = await page.locator("input").all()
        print(f"\nAll {len(inputs)} inputs:")
        for inp in inputs:
            t = await inp.get_attribute("type") or "text"
            n = await inp.get_attribute("name") or ""
            pid = await inp.get_attribute("id") or ""
            ph = await inp.get_attribute("placeholder") or ""
            vis = await inp.is_visible()
            print(f"  INPUT: type={t} name={n} id={pid} ph='{ph}' visible={vis}")
        
        # Tất cả buttons
        btns = await page.locator("button").all()
        print(f"\nAll {len(btns)} buttons:")
        for btn in btns:
            txt = (await btn.inner_text()).strip()
            t = await btn.get_attribute("type") or ""
            pid = await btn.get_attribute("id") or ""
            cls = await btn.get_attribute("class") or ""
            vis = await btn.is_visible()
            print(f"  BUTTON: text='{txt[:30]}' type={t} id={pid} class={cls[:40]} visible={vis}")
        
        # Forms
        forms = await page.locator("form").all()
        print(f"\nAll {len(forms)} forms:")
        for form in forms:
            action = await form.get_attribute("action") or ""
            method = await form.get_attribute("method") or ""
            print(f"  FORM: action={action} method={method}")
        
        await browser.close()

asyncio.run(main())
