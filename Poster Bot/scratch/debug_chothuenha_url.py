"""Tìm URL đăng tin đúng của chothuenha.com.vn"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Login first
        await page.goto("https://chothuenha.com.vn/dang-nhap", timeout=20000)
        await page.wait_for_timeout(2000)
        
        # Check DOM
        inputs = await page.locator("input").all()
        print("Login page inputs:")
        for inp in inputs[:8]:
            t = await inp.get_attribute("type") or "text"
            n = await inp.get_attribute("name") or ""
            pid = await inp.get_attribute("id") or ""
            ph = await inp.get_attribute("placeholder") or ""
            print(f"  INPUT: type={t} name={n} id={pid} ph='{ph}'")
        
        # Try login
        try:
            await page.fill("input[name='Phone'], input[type='tel'], input[placeholder*='điện thoại'], input[placeholder*='phone']", "0935723727")
        except Exception as e:
            print(f"  Phone fill error: {e}")
            try:
                # Maybe it's email
                await page.fill("input[type='email'], input[name='Email']", "binh.officedanang@gmail.com")
            except:
                pass
        
        try:
            await page.fill("input[name='Password'], input[type='password']", "Binh1995@")
        except Exception as e:
            print(f"  Password fill error: {e}")
        
        # Click login
        try:
            await page.click("button[type='submit']")
            await page.wait_for_timeout(5000)
            print(f"URL after login: {page.url}")
        except Exception as e:
            print(f"  Login click error: {e}")
        
        # Try different post URLs
        test_urls = [
            "https://chothuenha.com.vn/dang-tin",
            "https://chothuenha.com.vn/dang-tin.html",
            "https://chothuenha.com.vn/quan-ly",
            "https://chothuenha.com.vn/tai-khoan",
            "https://chothuenha.com.vn/tai-khoan/dang-tin",
            "https://chothuenha.com.vn/post",
            "https://chothuenha.com.vn/them-tin",
        ]
        for url in test_urls:
            try:
                r = await page.goto(url, timeout=8000)
                st = r.status if r else "?"
                title = await page.title()
                inputs_count = await page.locator("input[type='text'], input[type='email'], textarea").count()
                print(f"  URL: {url} -> {st} | '{title[:40]}' | {inputs_count} inputs")
            except Exception as e:
                print(f"  URL: {url} -> Error: {str(e)[:60]}")
        
        await browser.close()

asyncio.run(main())
