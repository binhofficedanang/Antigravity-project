import asyncio
from playwright.async_api import async_playwright

EMAIL = "binh.officedanang@gmail.com"
PHONE = "0935723727"
PASSWORD = "Binh1995@"
USERNAME = "binhofficedanang"
NAME = "Binh Office Da Nang"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        print("Loading vatgia register page...")
        await page.goto("https://www.vatgia.com/user/register", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        # Remove readonly from inputs if any
        await page.evaluate("""() => {
            document.querySelectorAll('input').forEach(el => el.removeAttribute('readonly'));
        }""")
        
        # Fill fields based on placeholders
        await page.fill("input[placeholder='Tên tài khoản']", USERNAME)
        await page.fill("input[placeholder='Họ và tên']", NAME)
        await page.fill("input[placeholder='Email']", EMAIL)
        await page.fill("input[placeholder='Mật khẩu']", PASSWORD)
        await page.fill("input[placeholder='Xác nhận mật khẩu']", PASSWORD)
        
        # Click register button
        await page.screenshot(path="vatgia_register_filled.png")
        await page.click("button:has-text('Đăng ký')")
        await page.wait_for_timeout(5000)
        
        print(f"URL after register attempt: {page.url}")
        await page.screenshot(path="vatgia_register_after.png")
        
        # Check if we can log in now
        print("Attempting login...")
        await page.goto("https://www.vatgia.com/user/login", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        await page.evaluate("""() => {
            document.querySelectorAll('input[placeholder="Tên đăng nhập"]').forEach(el => el.removeAttribute('readonly'));
            document.querySelectorAll('input[placeholder="Mật khẩu"]').forEach(el => el.removeAttribute('readonly'));
        }""")
        await page.fill("input[placeholder='Tên đăng nhập']", USERNAME) # Try username this time
        await page.fill("input[placeholder='Mật khẩu']", PASSWORD)
        await page.click("button.btn-login")
        await page.wait_for_timeout(5000)
        
        print(f"URL after login: {page.url}")
        await page.screenshot(path="vatgia_login_after_register.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
