import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def print_links_and_text(page, site_name, url):
    print(f"\n==========================================")
    print(f"ANALYZING SITE: {site_name} -> {url}")
    print(f"==========================================")
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(2000)
        
        # Current URL and Title
        print(f"  Current URL: {page.url}")
        print(f"  Title: {await page.title()}")
        
        # Dump all inputs
        inputs = await page.locator("input, select, textarea, button").all()
        print(f"  Inputs found: {len(inputs)}")
        for idx, inp in enumerate(inputs[:25]):
            tag = await inp.evaluate("el => el.tagName")
            name = await inp.get_attribute("name") or ""
            id_attr = await inp.get_attribute("id") or ""
            type_attr = await inp.get_attribute("type") or ""
            placeholder = await inp.get_attribute("placeholder") or ""
            is_vis = await inp.is_visible()
            val = await inp.get_attribute("value") or ""
            print(f"    [{idx}] <{tag}> name='{name}', id='{id_attr}', type='{type_attr}', placeholder='{placeholder}', visible={is_vis}, val='{val}'")
            
        # Dump all links with text
        links = await page.locator("a").all()
        print(f"  Total links: {len(links)}")
        printed_links = 0
        for l in links:
            href = await l.get_attribute("href") or ""
            text = await l.inner_text()
            text = text.strip().replace("\n", " ")
            if href.startswith("http") or href.startswith("/") or href.startswith("#"):
                # Print interesting links or first 20 links
                if any(w in text.lower() or w in href.lower() for w in ["nhap", "login", "dang-ky", "register", "post", "dang-tin", "thanhvien", "user", "profile"]):
                    print(f"    [Link] text='{text}' -> href='{href}'")
                    printed_links += 1
                elif printed_links < 15:
                    print(f"    [Link] (regular) text='{text}' -> href='{href}'")
                    printed_links += 1
                    
        # Check for visible text indicating error or success
        body_text = await page.inner_text("body")
        for line in body_text.split("\n"):
            line = line.strip()
            if any(w in line.lower() for w in ["sai mật khẩu", "không đúng", "thành công", "lỗi", "error", "invalid", "incorrect", "thất bại", "không tồn tại"]):
                print(f"    [Text match] '{line}'")
                
    except Exception as e:
        print(f"  Error: {e}")

async def test_vatgia_error(page):
    print("\n=== TESTING VATGIA LOGIN ERROR ===")
    await page.goto("https://www.vatgia.com/user/login", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    await page.evaluate("""() => {
        document.querySelectorAll('input[placeholder="Tên đăng nhập"]').forEach(el => el.removeAttribute('readonly'));
        document.querySelectorAll('input[placeholder="Mật khẩu"]').forEach(el => el.removeAttribute('readonly'));
    }""")
    await page.fill("input[placeholder='Tên đăng nhập']", "binh.officedanang@gmail.com")
    await page.fill("input[placeholder='Mật khẩu']", "Binh1995@")
    await page.click("button.btn-login")
    await page.wait_for_timeout(4000)
    print(f"  URL after: {page.url}")
    # Print error messages in vatgia
    validate_msgs = await page.locator(".validate-input").all_inner_texts()
    print(f"  Vatgia validation messages: {validate_msgs}")
    body_text = await page.inner_text("body")
    for line in body_text.split("\n"):
        if any(w in line.lower() for w in ["mật khẩu", "tài khoản", "đăng nhập", "lỗi", "không"]):
            print(f"    Line: {line}")

async def test_nhadatvn_error(page):
    print("\n=== TESTING NHADATVN LOGIN ERROR ===")
    await page.goto("https://nhadatvn.com.vn/thanh-vien-khu-vuc-toan-quoc/dang-nhap/", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    await page.evaluate("""() => {
        document.querySelectorAll('input[name="sodienthoai"]').forEach(el => {
            el.style.display = 'block';
            el.style.visibility = 'visible';
            el.removeAttribute('disabled');
        });
        document.querySelectorAll('input[name="password"]').forEach(el => {
            el.style.display = 'block';
            el.style.visibility = 'visible';
            el.removeAttribute('disabled');
        });
    }""")
    await page.fill("input[name='sodienthoai']", "0935723727")
    await page.fill("input[name='password']", "Binh1995@")
    await page.click("#login_feahfl button")
    await page.wait_for_timeout(4000)
    print(f"  URL after: {page.url}")
    body_text = await page.inner_text("body")
    for line in body_text.split("\n"):
        if any(w in line.lower() for w in ["mật khẩu", "điện thoại", "tài khoản", "đăng nhập", "không"]):
            print(f"    Line: {line}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        await print_links_and_text(page, "chonhadat24h.com", "https://chonhadat24h.com/")
        await print_links_and_text(page, "nhaongay.vn (direct)", "https://nhaongay.vn/dang-nhap")
        await print_links_and_text(page, "raovat.nhadat.vn", "http://raovat.nhadat.vn/")
        
        await test_vatgia_error(page)
        await test_nhadatvn_error(page)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
