"""Login chothuenha và tìm URL đăng tin sau login"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://chothuenha.com.vn/dang-nhap", timeout=20000)
        await page.wait_for_timeout(2000)
        
        # Login với selector đúng
        try:
            await page.fill("#login_input_telephone", "0935723727")
            await page.fill("#login_input_password", "Binh1995@")
            # Click btn_nut (type=button, không phải submit)
            await page.evaluate("document.querySelector('button.btn_nut').click()")
            await page.wait_for_timeout(5000)
            print(f"URL after login: {page.url}")
            print(f"Title: {await page.title()}")
        except Exception as e:
            print(f"Login error: {e}")
            return
        
        # Tìm link đăng tin sau login
        links = await page.locator("a[href*='dang-tin'], a:has-text('Đăng tin'), a[href*='them-tin']").all()
        print(f"\nPost links found: {len(links)}")
        for link in links[:5]:
            txt = (await link.inner_text()).strip()
            href = await link.get_attribute("href") or ""
            print(f"  LINK: text='{txt}' href={href}")
        
        # Thử URL tai-khoan/dang-tin
        for test_url in ["https://chothuenha.com.vn/tai-khoan/dang-tin", 
                         "https://chothuenha.com.vn/tai-khoan",
                         "https://chothuenha.com.vn/tai-khoan/tin-dang"]:
            r = await page.goto(test_url, timeout=10000)
            st = r.status if r else "?"
            title = await page.title()
            url_now = page.url
            inputs = await page.locator("input:visible, textarea:visible").count()
            print(f"  URL: {test_url} -> {st} | final={url_now} | title='{title[:50]}' | {inputs} inputs")
        
        await browser.close()

asyncio.run(main())
