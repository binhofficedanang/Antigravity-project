import asyncio
import os
import sys
from playwright.async_api import async_playwright

EMAIL = "binh.officedanang@gmail.com"
PHONE = "0935723727"
PASSWORD = "Binh1995@"
USERNAME = "binhofficedanang"

async def check_logged_in(page, check_type):
    # Standard check for logged in indicator
    body_text = await page.inner_text("body")
    lower_text = body_text.lower()
    
    indicators = ["đăng xuất", "thoát", "tài khoản", "profile", "chào", "xin chào", "member", "logout"]
    logged = any(ind in lower_text for ind in indicators)
    print(f"    [{check_type}] Logged in check indicators: {logged}")
    return logged

async def test_chovinh(page):
    print("\n=== TESTING CHOVINH.COM ===")
    await page.goto("https://chovinh.com/login/", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    # Try logging in
    await page.fill("#ctrl_pageLogin_login", EMAIL)
    await page.fill("#ctrl_pageLogin_password", PASSWORD)
    await page.locator("#ctrl_pageLogin_registered").check()
    await page.click("input[type='submit']")
    await page.wait_for_timeout(5000)
    
    logged = await check_logged_in(page, "CHOVINH")
    if logged:
        # Navigate to post page (standard forum is 11 or similar)
        # Standard rao vat thread creation page
        await page.goto("https://chovinh.com/forums/11/create-thread", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        print(f"    Post page URL: {page.url}")
        await page.screenshot(path="detail_chovinh_post_form.png")
        
        # Dump posting inputs
        inputs = await page.locator("input, select, textarea").all()
        for idx, inp in enumerate(inputs[:20]):
            tag = await inp.evaluate("el => el.tagName")
            name = await inp.get_attribute("name") or ""
            id_attr = await inp.get_attribute("id") or ""
            print(f"      [{idx}] <{tag}> name='{name}', id='{id_attr}'")
    else:
        print("    Failed to log in to chovinh.com")

async def test_cvt(page):
    print("\n=== TESTING CVT.VN ===")
    # Try username "binhofficedanang"
    for login_id in [USERNAME, EMAIL, PHONE]:
        print(f"  Trying login ID: {login_id}")
        await page.goto("https://cvt.vn/login/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.fill("#user_login", login_id)
        await page.fill("#user_pass", PASSWORD)
        await page.click("#wp-submit")
        await page.wait_for_timeout(4000)
        
        if "wp-login.php" not in page.url:
            print(f"    Success with ID: {login_id}! URL is: {page.url}")
            await page.screenshot(path="detail_cvt_logged_in.png")
            # Go to classifieds creation
            await page.goto("https://cvt.vn/wp-admin/post-new.php?post_type=classified", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            await page.screenshot(path="detail_cvt_post_form.png")
            return True
            
    print("    Failed all login combinations for cvt.vn")
    return False

async def test_nhaongay(page):
    print("\n=== TESTING NHAONGAY.VN ===")
    # Try different login IDs
    for login_id in [EMAIL, PHONE, USERNAME]:
        print(f"  Trying login ID: {login_id}")
        await page.goto("https://sellercenter.nhaongay.vn/sign-in", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.fill("input[name='email']", login_id) # The input field is name='email' but might accept phone/username
        await page.fill("input[name='password']", PASSWORD)
        await page.click("#kt_sign_in_submit")
        await page.wait_for_timeout(4000)
        
        if "sign-in" not in page.url:
            print(f"    Success with ID: {login_id}! URL is: {page.url}")
            await page.screenshot(path="detail_nhaongay_logged_in.png")
            return True
            
    print("    Failed all login combinations for nhaongay.vn")
    return False

async def test_nhadatvn(page):
    print("\n=== TESTING NHADATVN.COM.VN ===")
    for login_id in [PHONE, EMAIL, USERNAME]:
        print(f"  Trying login ID: {login_id}")
        await page.goto("https://nhadatvn.com.vn/thanh-vien-khu-vuc-toan-quoc/dang-nhap/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        await page.evaluate(f"""() => {{
            const phone = document.querySelector("input[name='sodienthoai']");
            const pass = document.querySelector("input[name='password']");
            if (phone) phone.value = "{login_id}";
            if (pass) pass.value = "{PASSWORD}";
        }}""")
        await page.evaluate("""() => {
            const btn = document.querySelector("#login_feahfl button") || document.querySelector("#login_feahfl input[type='submit']");
            if (btn) btn.click();
        }""")
        await page.wait_for_timeout(4000)
        
        body_text = await page.inner_text("body")
        if "Đăng nhập thất bại" not in body_text:
            print(f"    Success with ID: {login_id}! URL is: {page.url}")
            await page.screenshot(path="detail_nhadatvn_logged_in.png")
            return True
            
    print("    Failed all login combinations for nhadatvn.com.vn")
    return False

async def test_vatgia_post(page):
    print("\n=== TESTING VATGIA.COM POST tin ===")
    await page.goto("https://www.vatgia.com/user/login", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    await page.evaluate("""() => {
        document.querySelectorAll('input[placeholder="Tên đăng nhập"]').forEach(el => el.removeAttribute('readonly'));
        document.querySelectorAll('input[placeholder="Mật khẩu"]').forEach(el => el.removeAttribute('readonly'));
    }""")
    await page.fill("input[placeholder='Tên đăng nhập']", EMAIL)
    await page.fill("input[placeholder='Mật khẩu']", PASSWORD)
    await page.click("button.btn-login")
    await page.wait_for_timeout(4000)
    
    # Go to raovat posting URL
    print("  Navigating to raovat posting page...")
    await page.goto("https://www.vatgia.com/raovat/dangtin", wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)
    print(f"    Post URL: {page.url}")
    await page.screenshot(path="detail_vatgia_post_form.png")
    
    inputs = await page.locator("input, select, textarea, button").all()
    print(f"    Inputs count on vatgia post page: {len(inputs)}")
    for idx, inp in enumerate(inputs[:25]):
        tag = await inp.evaluate("el => el.tagName")
        name = await inp.get_attribute("name") or ""
        placeholder = await inp.get_attribute("placeholder") or ""
        print(f"      [{idx}] <{tag}> name='{name}', placeholder='{placeholder}'")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        await test_chovinh(page)
        await test_cvt(page)
        await test_nhaongay(page)
        await test_nhadatvn(page)
        await test_vatgia_post(page)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
