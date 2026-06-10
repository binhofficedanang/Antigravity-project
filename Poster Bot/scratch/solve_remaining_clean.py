import asyncio
import os
import sys
from playwright.async_api import async_playwright

EMAIL = "binh.officedanang@gmail.com"
PHONE = "0935723727"
PASSWORD = "Binh1995@"
USERNAME = "binhofficedanang"
NAME = "Binh Office Da Nang"

async def test_chonhadat24h(page):
    print("\n--- CHONHADAT24H.COM ---")
    try:
        await page.goto("https://chonhadat24h.com/", wait_until="domcontentloaded", timeout=25000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path="clean_chonhadat_home.png")
        
        links = await page.locator("a").all()
        print(f"  Total links: {len(links)}")
        for l in links:
            href = await l.get_attribute("href") or ""
            text = await l.inner_text()
            text = text.strip().replace("\n", " ")
            if text:
                if any(w in text.lower() or w in href.lower() for w in ["nhap", "login", "dang-ky", "register", "thanhvien", "user", "post", "dang-tin"]):
                    print(f"    Link: '{text}' -> href='{href}'")
                    
        # Let's try direct subpaths
        for path in ["/vn/login.php", "/login.php", "/login.html", "/member/login", "/thanh-vien/dang-nhap", "/vn/member.php"]:
            try:
                url = "https://chonhadat24h.com" + path
                print(f"  Trying subpath: {url}")
                resp = await page.goto(url, wait_until="domcontentloaded", timeout=10000)
                if resp and resp.status == 200:
                    print(f"    Found active subpath: {page.url}")
                    await page.screenshot(path=f"clean_chonhadat_subpath_{path.replace('/', '_')}.png")
                    inputs = await page.locator("input").all()
                    print(f"    Inputs count: {len(inputs)}")
                    for idx, inp in enumerate(inputs):
                        print(f"      [{idx}] name='{await inp.get_attribute('name')}', type='{await inp.get_attribute('type')}'")
            except Exception as e_path:
                print(f"    Failed {path}: {e_path}")
    except Exception as e:
        print(f"  Failed chonhadat: {e}")

async def test_chovinh(page):
    print("\n--- CHOVINH.COM ---")
    try:
        # Check login
        await page.goto("https://chovinh.com/login/", wait_until="domcontentloaded", timeout=25000)
        await page.wait_for_timeout(2000)
        await page.fill("#ctrl_pageLogin_login", EMAIL)
        await page.fill("#ctrl_pageLogin_password", PASSWORD)
        await page.locator("#ctrl_pageLogin_registered").check()
        await page.click("input[type='submit']")
        await page.wait_for_timeout(4000)
        
        print(f"  URL after login attempt: {page.url}")
        body_text = await page.inner_text("body")
        if "không đúng" in body_text.lower() or "incorrect" in body_text.lower() or "error" in body_text.lower():
            print("  Login failed on chovinh.com. Checking registration...")
            await page.goto("https://chovinh.com/register/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="clean_chovinh_register.png")
            # Dump inputs
            inputs = await page.locator("input, select, textarea").all()
            print(f"  Registration inputs: {len(inputs)}")
            for idx, inp in enumerate(inputs[:15]):
                tag = await inp.evaluate("el => el.tagName")
                name = await inp.get_attribute("name") or ""
                placeholder = await inp.get_attribute("placeholder") or ""
                type_attr = await inp.get_attribute("type") or ""
                print(f"    [{idx}] <{tag}> name='{name}', type='{type_attr}', placeholder='{placeholder}'")
        else:
            print("  Login succeeded or did not show error. Checking post page...")
            await page.goto("https://chovinh.com/forums/11/create-thread", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            await page.screenshot(path="clean_chovinh_post.png")
    except Exception as e:
        print(f"  Failed chovinh: {e}")

async def test_cvt(page):
    print("\n--- CVT.VN ---")
    try:
        await page.goto("https://cvt.vn/login/", wait_until="domcontentloaded", timeout=25000)
        await page.wait_for_timeout(2000)
        await page.fill("#user_login", EMAIL)
        await page.fill("#user_pass", PASSWORD)
        await page.click("#wp-submit")
        await page.wait_for_timeout(4000)
        
        print(f"  URL after login attempt: {page.url}")
        body_text = await page.inner_text("body")
        if "error" in body_text.lower() or "không đúng" in body_text.lower() or "incorrect" in body_text.lower() or "wp-login.php" in page.url:
            print("  Login failed on cvt.vn. Checking registration...")
            await page.goto("https://cvt.vn/wp-login.php?action=register", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="clean_cvt_register.png")
            # Dump inputs
            inputs = await page.locator("input, select, textarea").all()
            print(f"  Registration inputs: {len(inputs)}")
            for idx, inp in enumerate(inputs[:15]):
                tag = await inp.evaluate("el => el.tagName")
                name = await inp.get_attribute("name") or ""
                placeholder = await inp.get_attribute("placeholder") or ""
                type_attr = await inp.get_attribute("type") or ""
                print(f"    [{idx}] <{tag}> name='{name}', type='{type_attr}', placeholder='{placeholder}'")
        else:
            print("  Login succeeded or did not show error. Checking post page...")
            await page.goto("https://cvt.vn/wp-admin/post-new.php?post_type=classified", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            await page.screenshot(path="clean_cvt_post.png")
    except Exception as e:
        print(f"  Failed cvt: {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        await test_chonhadat24h(page)
        await test_chovinh(page)
        await test_cvt(page)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
