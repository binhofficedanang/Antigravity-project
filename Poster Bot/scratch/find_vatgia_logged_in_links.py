import asyncio
from playwright.async_api import async_playwright

EMAIL = "binh.officedanang@gmail.com"
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
        
        # Go to login
        await page.goto("https://www.vatgia.com/user/login", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        # Remove readonly
        await page.evaluate("""() => {
            document.querySelectorAll('input[placeholder="Tên đăng nhập"]').forEach(el => el.removeAttribute('readonly'));
            document.querySelectorAll('input[placeholder="Mật khẩu"]').forEach(el => el.removeAttribute('readonly'));
        }""")
        await page.fill("input[placeholder='Tên đăng nhập']", EMAIL)
        await page.fill("input[placeholder='Mật khẩu']", PASSWORD)
        await page.click("button.btn-login")
        await page.wait_for_timeout(5000)
        
        print(f"Logged in. Current URL: {page.url}")
        await page.screenshot(path="vatgia_logged_in_state.png")
        
        # Dump all links when logged in on vatgia.com
        links = await page.locator("a").all()
        print(f"Total links when logged in: {len(links)}")
        for idx, l in enumerate(links):
            text = await l.inner_text()
            href = await l.get_attribute("href") or ""
            text = text.strip().replace("\n", " ")
            if text or href:
                if any(w in text.lower() or w in href.lower() for w in ["dang", "post", "tin", "thanhvien", "user", "up"]):
                    print(f"  [{idx}] text='{text}' -> href='{href}'")
                    
        # Let's check raovat homepage when logged in
        await page.goto("https://www.vatgia.com/raovat/", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        print(f"Raovat URL when logged in: {page.url}")
        await page.screenshot(path="vatgia_raovat_logged_in.png")
        
        links_rv = await page.locator("a").all()
        print(f"Total links on raovat home when logged in: {len(links_rv)}")
        for idx, l in enumerate(links_rv):
            text = await l.inner_text()
            href = await l.get_attribute("href") or ""
            text = text.strip().replace("\n", " ")
            if text or href:
                if any(w in text.lower() or w in href.lower() for w in ["dang", "post", "tin", "thanhvien", "user", "up"]):
                    print(f"  [Raovat Link] [{idx}] text='{text}' -> href='{href}'")
                    
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
