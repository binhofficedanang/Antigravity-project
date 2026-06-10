import asyncio
import os
import sys
import time
from playwright.async_api import async_playwright

EMAIL = "binh.officedanang@gmail.com"
PHONE = "0935723727"
PASSWORD = "Binh1995@"
USERNAME = "binhofficedanang"

async def test_vatgia(page):
    print("\n--- VATGIA.COM ---")
    await page.goto("https://www.vatgia.com/user/login", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    # Remove readonly
    await page.evaluate("""() => {
        document.querySelectorAll('input[placeholder="Tên đăng nhập"]').forEach(el => el.removeAttribute('readonly'));
        document.querySelectorAll('input[placeholder="Mật khẩu"]').forEach(el => el.removeAttribute('readonly'));
    }""")
    
    # Fill fields
    await page.fill("input[placeholder='Tên đăng nhập']", EMAIL)
    await page.fill("input[placeholder='Mật khẩu']", PASSWORD)
    
    # Click login via JS to be safe
    await page.evaluate("""() => {
        const btn = document.querySelector("button.btn-login") || document.querySelector("button:has-text('Đăng nhập')");
        if (btn) btn.click();
    }""")
    await page.wait_for_timeout(6000)
    
    print(f"  URL after login: {page.url}")
    # Check if there is a logout link or personal link
    body_text = await page.inner_text("body")
    print(f"  Is 'Thoát' or 'Đăng xuất' or profile in page? {'thoát' in body_text.lower() or 'đăng xuất' in body_text.lower() or 'chào' in body_text.lower()}")
    await page.screenshot(path="solve_vatgia_after.png")
    
    # Let's check register page for captcha
    print("  Checking vatgia register page...")
    await page.goto("https://www.vatgia.com/user/register", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    await page.screenshot(path="solve_vatgia_register.png")
    inputs = await page.locator("input, select, textarea, img").all()
    print(f"  Inputs/images on register page: {len(inputs)}")
    for idx, inp in enumerate(inputs[:20]):
        tag = await inp.evaluate("el => el.tagName")
        placeholder = await inp.get_attribute("placeholder") or ""
        src = await inp.get_attribute("src") or ""
        name = await inp.get_attribute("name") or ""
        print(f"    [{idx}] <{tag}> name='{name}', placeholder='{placeholder}', src='{src}'")

async def test_nhadatvn(page):
    print("\n--- NHADATVN.COM.VN ---")
    await page.goto("https://nhadatvn.com.vn/thanh-vien-khu-vuc-toan-quoc/dang-nhap/", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    # Fill phone and password (even if Playwright thinks they are invisible)
    await page.evaluate(f"""() => {{
        const phone = document.querySelector("input[name='sodienthoai']");
        const pass = document.querySelector("input[name='password']");
        if (phone) phone.value = "{PHONE}";
        if (pass) pass.value = "{PASSWORD}";
    }}""")
    
    # Click button via JS
    await page.evaluate("""() => {
        const btn = document.querySelector("#login_feahfl button") || document.querySelector("#login_feahfl input[type='submit']");
        if (btn) btn.click();
    }""")
    await page.wait_for_timeout(6000)
    
    print(f"  URL after login: {page.url}")
    # Print any text on page related to login errors
    body_text = await page.inner_text("body")
    for line in body_text.split("\n"):
        if any(w in line.lower() for w in ["mật khẩu", "điện thoại", "tài khoản", "đăng nhập", "không"]):
            print(f"    Line: {line}")
    await page.screenshot(path="solve_nhadatvn_after.png")
    
    # Try registration if needed
    print("  Checking registration page...")
    await page.goto("https://nhadatvn.com.vn/register.htm", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    await page.screenshot(path="solve_nhadatvn_register.png")

async def test_chonhadat24h(page):
    print("\n--- CHONHADAT24H.COM ---")
    # Let's load the login page and wait for 10 seconds to see if it loads dynamically via javascript
    await page.goto("https://chonhadat24h.com/dang-nhap", wait_until="domcontentloaded")
    print("  Waiting 10 seconds for dynamic login form...")
    await page.wait_for_timeout(10000)
    
    # Let's search for form and input elements
    inputs = await page.locator("input, select, textarea, button").all()
    print(f"  Inputs found: {len(inputs)}")
    for idx, inp in enumerate(inputs):
        tag = await inp.evaluate("el => el.tagName")
        name = await inp.get_attribute("name") or ""
        id_attr = await inp.get_attribute("id") or ""
        placeholder = await inp.get_attribute("placeholder") or ""
        print(f"    [{idx}] <{tag}> name='{name}', id='{id_attr}', placeholder='{placeholder}'")
        
    await page.screenshot(path="solve_chonhadat_after_wait.png")
    
    # If still not found, let's check homepage and search for the login button
    await page.goto("https://chonhadat24h.com/", wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)
    await page.screenshot(path="solve_chonhadat_home.png")

async def test_nhaongay(page):
    print("\n--- NHAONGAY.VN ---")
    # Nhaongay seller center
    await page.goto("https://sellercenter.nhaongay.vn/", wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)
    print(f"  Sellercenter URL: {page.url}")
    print(f"  Sellercenter Title: {await page.title()}")
    await page.screenshot(path="solve_nhaongay_seller.png")
    
    inputs = await page.locator("input, select, textarea, button").all()
    print(f"  Inputs found on seller center: {len(inputs)}")
    for idx, inp in enumerate(inputs[:25]):
        tag = await inp.evaluate("el => el.tagName")
        name = await inp.get_attribute("name") or ""
        id_attr = await inp.get_attribute("id") or ""
        placeholder = await inp.get_attribute("placeholder") or ""
        type_attr = await inp.get_attribute("type") or ""
        print(f"    [{idx}] <{tag}> name='{name}', id='{id_attr}', type='{type_attr}', placeholder='{placeholder}'")
        
    # Attempt login on sellercenter if inputs are username/password or phone/password
    # Let's check if there's username and password inputs
    username_field = page.locator("input[type='text'], input[type='email'], input[placeholder*='Email'], input[placeholder*='thoại']").first
    password_field = page.locator("input[type='password']").first
    submit_btn = page.locator("button[type='submit'], button:has-text('Đăng nhập'), input[type='submit']").first
    
    if await username_field.count() > 0 and await password_field.count() > 0:
        print("  Found login fields on seller center. Attempting login...")
        await username_field.fill(EMAIL)
        await password_field.fill(PASSWORD)
        await page.screenshot(path="solve_nhaongay_filled.png")
        if await submit_btn.count() > 0:
            await submit_btn.click()
        else:
            await password_field.press("Enter")
        await page.wait_for_timeout(6000)
        print(f"  Sellercenter URL after login: {page.url}")
        await page.screenshot(path="solve_nhaongay_after_login.png")

async def test_nhadat_vn(page):
    print("\n--- NHADAT.VN ---")
    await page.goto("http://raovat.nhadat.vn/", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    # Fill login fields
    await page.fill("#navbar_username", USERNAME) # Try username first
    # Click hint password to make the password field visible/active
    try:
        await page.click("#navbar_password_hint")
    except:
        pass
    await page.fill("#navbar_password", PASSWORD)
    await page.screenshot(path="solve_nhadat_filled.png")
    
    # Click submit
    await page.click("input[type='submit'][value='Đăng nhập']")
    await page.wait_for_timeout(6000)
    
    print(f"  URL after login: {page.url}")
    print(f"  Title: {await page.title()}")
    await page.screenshot(path="solve_nhadat_after_login.png")
    
    # Check if we can navigate to post tin page
    await page.goto("https://raovat.nhadat.vn/dangtin.html", wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)
    print(f"  Post tin URL: {page.url}")
    await page.screenshot(path="solve_nhadat_post_page.png")
    
    # Let's print out form elements on posting page
    inputs = await page.locator("input, select, textarea, button").all()
    print(f"  Inputs on post page: {len(inputs)}")
    for idx, inp in enumerate(inputs[:25]):
        tag = await inp.evaluate("el => el.tagName")
        name = await inp.get_attribute("name") or ""
        id_attr = await inp.get_attribute("id") or ""
        placeholder = await inp.get_attribute("placeholder") or ""
        type_attr = await inp.get_attribute("type") or ""
        print(f"    [{idx}] <{tag}> name='{name}', id='{id_attr}', type='{type_attr}', placeholder='{placeholder}'")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        await test_vatgia(page)
        await test_nhadatvn(page)
        await test_chonhadat24h(page)
        await test_nhaongay(page)
        await test_nhadat_vn(page)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
