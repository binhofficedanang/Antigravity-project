import asyncio
import os
from playwright.async_api import async_playwright

EMAIL = "binh.officedanang@gmail.com"
PHONE = "0935723727"
PASSWORD = "Binh1995@"
USERNAME = "binhofficedanang"

async def investigate_vatgia(page):
    print("\n=== INVESTIGATING VATGIA.COM ===")
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
    
    # Navigate to raovat homepage
    await page.goto("https://www.vatgia.com/raovat/", wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)
    print(f"  Raovat URL: {page.url}")
    await page.screenshot(path="investigate_vatgia_raovat_home.png")
    
    # Search for all links on raovat homepage
    links = await page.locator("a").all()
    print(f"  Total links on raovat home: {len(links)}")
    for l in links:
        href = await l.get_attribute("href") or ""
        text = await l.inner_text()
        text = text.strip().replace("\n", " ")
        if any(w in text.lower() or w in href.lower() for w in ["dangtin", "dang-tin", "post", "dang_tin", "rao-vat", "them-tin"]):
            print(f"    Link: '{text}' -> href='{href}'")

async def investigate_chovinh(page):
    print("\n=== INVESTIGATING CHOVINH.COM ===")
    await page.goto("https://chovinh.com/register/", wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)
    await page.screenshot(path="investigate_chovinh_register.png")
    
    # Check for any captcha or recaptcha in HTML
    content = await page.content()
    print(f"  Is recaptcha in HTML? {'recaptcha' in content.lower()}")
    print(f"  Is hcaptcha in HTML? {'hcaptcha' in content.lower()}")
    print(f"  Is captcha in HTML? {'captcha' in content.lower()}")
    
    # Print all input/img tags to see if there is an image captcha
    inputs = await page.locator("input, select, textarea, img").all()
    print(f"  Inputs/Images count: {len(inputs)}")
    for idx, inp in enumerate(inputs):
        tag = await inp.evaluate("el => el.tagName")
        name = await inp.get_attribute("name") or ""
        id_attr = await inp.get_attribute("id") or ""
        src = await inp.get_attribute("src") or ""
        type_attr = await inp.get_attribute("type") or ""
        print(f"    [{idx}] <{tag}> name='{name}', id='{id_attr}', type='{type_attr}', src='{src}'")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        await investigate_vatgia(page)
        await investigate_chovinh(page)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
