"""Tìm đúng cách login nhachothue.vn"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()
        
        await page.goto("https://nhachothue.vn/", timeout=30000)
        await page.wait_for_timeout(2000)
        
        # In tất cả button
        btns = await page.locator("button, a.btn, a[href*='login'], a[href*='dang-nhap']").all()
        print(f"\nFound {len(btns)} clickable elements:")
        for btn in btns[:15]:
            txt = (await btn.inner_text()).strip()
            pid = await btn.get_attribute("id") or ""
            cls = await btn.get_attribute("class") or ""
            href = await btn.get_attribute("href") or ""
            print(f"  text='{txt[:30]}' id={pid} href={href[:40]} class={cls[:30]}")
        
        # Tìm nút đăng nhập
        login_links = await page.locator("a:has-text('Đăng nhập'), button:has-text('Đăng nhập')").all()
        print(f"\nLogin links found: {len(login_links)}")
        if login_links:
            print("  Clicking first login link...")
            await login_links[0].click()
            await page.wait_for_timeout(2000)
            # Kiểm tra lại inputs sau click
            inputs = await page.locator("input:visible").all()
            print(f"  Visible inputs after click: {len(inputs)}")
            for inp in inputs[:5]:
                t = await inp.get_attribute("type") or "text"
                pid = await inp.get_attribute("id") or ""
                print(f"    INPUT: type={t} id={pid}")
        
        await page.screenshot(path="nhachothue_debug.png")
        await browser.close()

asyncio.run(main())
