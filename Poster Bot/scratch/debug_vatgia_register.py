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
        page = await browser.new_page()
        await page.goto("https://www.vatgia.com/user/register", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        await page.evaluate("""() => {
            document.querySelectorAll('input').forEach(el => el.removeAttribute('readonly'));
        }""")
        
        await page.fill("input[placeholder='Tên tài khoản']", USERNAME)
        await page.fill("input[placeholder='Họ và tên']", NAME)
        await page.fill("input[placeholder='Email']", EMAIL)
        await page.fill("input[placeholder='Mật khẩu']", PASSWORD)
        await page.fill("input[placeholder='Xác nhận mật khẩu']", PASSWORD)
        
        await page.click("button:has-text('Đăng ký')")
        await page.wait_for_timeout(4000)
        
        # Check validation error texts
        errs = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.validate-input')).map(el => (el.innerText || '').trim());
        }""")
        print(f"Validation errors: {errs}")
        
        # Print other error containers if any
        body_text = await page.inner_text("body")
        for line in body_text.split("\n"):
            line = line.strip()
            if any(w in line.lower() for w in ["đã tồn tại", "trùng", "yêu cầu", "lỗi", "không", "error", "valid"]):
                print(f"  Line: {line}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
