import asyncio
import os
import sys
import time
from playwright.async_api import async_playwright

EMAIL = "binh.officedanang@gmail.com"
PHONE = "0935723727"
PASSWORD = "Binh1995@"
USERNAME = "binhofficedanang"
NAME = "Binh Office Da Nang"

async def check_nhadatvn_register(page):
    print("\n--- NHADATVN.COM.VN REGISTER/LOGIN ---")
    await page.goto("https://nhadatvn.com.vn/register.htm", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    await page.screenshot(path="detail_nhadatvn_register_form.png")
    
    # Dump registration inputs
    inputs = await page.locator("input, select, textarea, button").all()
    print(f"  Inputs on register page: {len(inputs)}")
    for idx, inp in enumerate(inputs[:15]):
        tag = await inp.evaluate("el => el.tagName")
        name = await inp.get_attribute("name") or ""
        id_attr = await inp.get_attribute("id") or ""
        placeholder = await inp.get_attribute("placeholder") or ""
        type_attr = await inp.get_attribute("type") or ""
        print(f"    [{idx}] <{tag}> name='{name}', id='{id_attr}', type='{type_attr}', placeholder='{placeholder}'")
        
    # Attempt registration
    print("  Attempting registration...")
    await page.evaluate(f"""() => {{
        const fields = {{
            'hoten': '{NAME}',
            'sodienthoai': '{PHONE}',
            'email': '{EMAIL}',
            'password': '{PASSWORD}',
            're-password': '{PASSWORD}'
        }};
        for (const [name, val] of Object.entries(fields)) {{
            const el = document.querySelector(`input[name="${{name}}"]`);
            if (el) el.value = val;
        }}
    }}""")
    await page.screenshot(path="detail_nhadatvn_register_filled.png")
    # Click register
    await page.evaluate("""() => {
        const btn = document.querySelector("#formregisterbds button") || document.querySelector("button[type='submit']");
        if (btn) btn.click();
    }""")
    await page.wait_for_timeout(5000)
    print(f"  URL after register: {page.url}")
    await page.screenshot(path="detail_nhadatvn_register_after.png")

async def check_nhaongay_register(page):
    print("\n--- NHAONGAY.VN REGISTER/LOGIN ---")
    await page.goto("https://sellercenter.nhaongay.vn/sign-up", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    await page.screenshot(path="detail_nhaongay_register_form.png")
    
    # Dump registration inputs
    inputs = await page.locator("input, select, textarea, button").all()
    print(f"  Inputs on register page: {len(inputs)}")
    for idx, inp in enumerate(inputs[:15]):
        tag = await inp.evaluate("el => el.tagName")
        name = await inp.get_attribute("name") or ""
        placeholder = await inp.get_attribute("placeholder") or ""
        type_attr = await inp.get_attribute("type") or ""
        print(f"    [{idx}] <{tag}> name='{name}', type='{type_attr}', placeholder='{placeholder}'")
        
    # Attempt registration
    print("  Attempting registration...")
    await page.fill("input[name='name']", NAME)
    await page.fill("input[name='phone']", PHONE)
    await page.fill("input[name='email']", EMAIL)
    await page.fill("input[name='password']", PASSWORD)
    await page.fill("input[name='password_confirmation']", PASSWORD)
    # Check checkbox if exists
    toc = page.locator("input[type='checkbox']").first
    if await toc.count() > 0:
        await toc.check()
    await page.screenshot(path="detail_nhaongay_register_filled.png")
    await page.click("button[type='submit']")
    await page.wait_for_timeout(5000)
    print(f"  URL after register: {page.url}")
    await page.screenshot(path="detail_nhaongay_register_after.png")

async def check_chonhadat24h(page):
    print("\n--- CHONHADAT24H.COM ---")
    await page.goto("https://chonhadat24h.com/", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    # Dump all text links with any text to see if there's a login popup or link
    links = await page.locator("a").all()
    print(f"  Total links on homepage: {len(links)}")
    for l in links:
        href = await l.get_attribute("href") or ""
        text = await l.inner_text()
        text = text.strip().replace("\n", " ")
        if text:
            if any(w in text.lower() or w in href.lower() for w in ["nhap", "login", "dang-ky", "register", "thanhvien", "user", "post", "dang-tin"]):
                print(f"    Link: '{text}' -> href='{href}'")

async def check_chovinh(page):
    print("\n--- CHOVINH.COM REGISTER/LOGIN ---")
    await page.goto("https://chovinh.com/register/", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    await page.screenshot(path="detail_chovinh_register.png")
    
    # Dump registration inputs
    inputs = await page.locator("input, select, textarea, button").all()
    print(f"  Inputs on register page: {len(inputs)}")
    for idx, inp in enumerate(inputs[:15]):
        tag = await inp.evaluate("el => el.tagName")
        name = await inp.get_attribute("name") or ""
        placeholder = await inp.get_attribute("placeholder") or ""
        type_attr = await inp.get_attribute("type") or ""
        print(f"    [{idx}] <{tag}> name='{name}', type='{type_attr}', placeholder='{placeholder}'")

async def check_cvt(page):
    print("\n--- CVT.VN REGISTER/LOGIN ---")
    await page.goto("https://cvt.vn/wp-login.php?action=register", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    await page.screenshot(path="detail_cvt_register.png")
    
    # Dump registration inputs
    inputs = await page.locator("input, select, textarea, button").all()
    print(f"  Inputs on register page: {len(inputs)}")
    for idx, inp in enumerate(inputs[:15]):
        tag = await inp.evaluate("el => el.tagName")
        name = await inp.get_attribute("name") or ""
        placeholder = await inp.get_attribute("placeholder") or ""
        type_attr = await inp.get_attribute("type") or ""
        print(f"    [{idx}] <{tag}> name='{name}', type='{type_attr}', placeholder='{placeholder}'")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        await check_nhadatvn_register(page)
        await check_nhaongay_register(page)
        await check_chonhadat24h(page)
        await check_chovinh(page)
        await check_cvt(page)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
