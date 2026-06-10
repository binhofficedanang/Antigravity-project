import asyncio
import os
import sys
import time
from playwright.async_api import async_playwright

EMAIL = "binh.officedanang@gmail.com"
PHONE = "0935723727"
PASSWORD = "Binh1995@"
USERNAME = "binhofficedanang"

async def dump_inputs(page):
    inputs = await page.locator("input, button, select, textarea").all()
    print(f"  Inputs on page: {len(inputs)}")
    for idx, inp in enumerate(inputs[:25]):
        try:
            tag = await inp.evaluate("el => el.tagName")
            name = await inp.get_attribute("name") or ""
            id_attr = await inp.get_attribute("id") or ""
            type_attr = await inp.get_attribute("type") or ""
            placeholder = await inp.get_attribute("placeholder") or ""
            is_vis = await inp.is_visible()
            readonly = await inp.get_attribute("readonly") or ""
            print(f"    [{idx}] <{tag}> name='{name}', id='{id_attr}', type='{type_attr}', placeholder='{placeholder}', visible={is_vis}, readonly='{readonly}'")
        except Exception as e:
            print(f"    [{idx}] Error: {e}")

async def inspect_chonhadat24h(page):
    print("\n--- chonhadat24h.com ---")
    await page.goto("https://chonhadat24h.com/", wait_until="domcontentloaded", timeout=25000)
    await page.wait_for_timeout(2000)
    await page.screenshot(path="detail_chonhadat_home.png")
    
    # Try to find the login button using text search or specific classes
    found = False
    for text in ["Đăng nhập", "đăng nhập", "Dang nhap", "dang nhap"]:
        loc = page.get_by_text(text)
        if await loc.count() > 0:
            print(f"  Found login text: '{text}'")
            # Let's find links containing dang-nhap
            links = await page.locator("a[href*='dang-nhap'], a[href*='login']").all()
            if links:
                href = await links[0].get_attribute("href")
                print(f"  Found login link href: {href}")
                await page.goto(href if href.startswith("http") else "https://chonhadat24h.com" + href, wait_until="domcontentloaded")
                found = True
                break
    
    if not found:
        # Go directly to login url
        print("  Going directly to login URL")
        await page.goto("https://chonhadat24h.com/dang-nhap", wait_until="domcontentloaded")
        
    await page.wait_for_timeout(3000)
    print(f"  Current URL: {page.url}")
    await page.screenshot(path="detail_chonhadat_login_page.png")
    await dump_inputs(page)

async def inspect_nhaongay(page):
    print("\n--- nhaongay.vn ---")
    await page.goto("https://nhaongay.vn/", wait_until="domcontentloaded", timeout=25000)
    await page.wait_for_timeout(2000)
    await page.screenshot(path="detail_nhaongay_home.png")
    
    # Find login button on homepage
    login_btn = None
    for sel in ["a[href*='dang-nhap']", "a[href*='login']", "a.btn-login"]:
        if await page.locator(sel).count() > 0:
            login_btn = page.locator(sel).first
            print(f"  Found login button with selector: {sel}")
            break
            
    if not login_btn:
        # Try finding by text
        loc = page.get_by_text("Đăng nhập")
        if await loc.count() > 0:
            login_btn = loc.first
            print("  Found login button by text 'Đăng nhập'")
            
    if login_btn:
        print("  Clicking login button...")
        await login_btn.click()
        await page.wait_for_timeout(4000)
        await page.screenshot(path="detail_nhaongay_modal.png")
    else:
        print("  Could not find login button on homepage.")
        
    print(f"  Current URL: {page.url}")
    await dump_inputs(page)

async def inspect_nhadat_vn(page):
    print("\n--- nhadat.vn ---")
    await page.goto("https://nhadat.vn/", wait_until="domcontentloaded", timeout=25000)
    await page.wait_for_timeout(2000)
    await page.screenshot(path="detail_nhadat_home.png")
    
    login_link = None
    for sel in ["a[href*='dang-nhap']", "a[href*='login']", "a[href*='signin']"]:
        if await page.locator(sel).count() > 0:
            login_link = page.locator(sel).first
            print(f"  Found login link with selector: {sel}")
            break
            
    if login_link:
        href = await login_link.get_attribute("href")
        print(f"  Login link href: {href}")
        await page.goto(href if href.startswith("http") else "https://nhadat.vn" + href, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="detail_nhadat_login_page.png")
    else:
        print("  Could not find login link on homepage. Trying direct url.")
        await page.goto("https://nhadat.vn/login", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="detail_nhadat_login_direct.png")
        
    print(f"  Current URL: {page.url}")
    await dump_inputs(page)

async def inspect_nhadatvn_com_vn(page):
    print("\n--- nhadatvn.com.vn ---")
    await page.goto("https://nhadatvn.com.vn/", wait_until="domcontentloaded", timeout=25000)
    await page.wait_for_timeout(2000)
    await page.screenshot(path="detail_nhadatvn_home.png")
    
    login_btn = None
    for sel in ["a[href*='dang-nhap']", "a[href*='login']"]:
        if await page.locator(sel).count() > 0:
            login_btn = page.locator(sel).first
            print(f"  Found login link with selector: {sel}")
            break
            
    if login_btn:
        print("  Clicking login button...")
        await login_btn.click()
        await page.wait_for_timeout(3000)
        await page.screenshot(path="detail_nhadatvn_clicked.png")
    else:
        print("  Could not find login link on homepage. Trying direct url.")
        await page.goto("https://nhadatvn.com.vn/thanh-vien/dang-nhap.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="detail_nhadatvn_login_direct.png")
        
    print(f"  Current URL: {page.url}")
    await dump_inputs(page)

async def inspect_vatgia(page):
    print("\n--- vatgia.com ---")
    await page.goto("https://www.vatgia.com/user/login", wait_until="domcontentloaded", timeout=25000)
    await page.wait_for_timeout(2000)
    await page.screenshot(path="detail_vatgia_login.png")
    await dump_inputs(page)
    
    # Let's inspect the page content around the inputs
    html = await page.content()
    with open("vatgia_login_page.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("  Saved vatgia login HTML for inspection.")

async def inspect_chovinh_post(page):
    print("\n--- chovinh.com login status & post ---")
    try:
        await page.goto("https://chovinh.com/login/", wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(2000)
        await page.fill("#ctrl_pageLogin_login", EMAIL)
        await page.fill("#ctrl_pageLogin_password", PASSWORD)
        await page.locator("#ctrl_pageLogin_registered").check()
        await page.click("input[type='submit']")
        await page.wait_for_timeout(5000)
        print(f"  URL after login click: {page.url}")
        await page.screenshot(path="detail_chovinh_after_login.png")
        
        # Navigate to homepage and check for posting links
        await page.goto("https://chovinh.com/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="detail_chovinh_home_logged_in.png")
        
        post_links = await page.locator("a[href*='dangtin'], a[href*='dang-tin'], a[href*='create-thread']").all()
        print(f"  Post tin links found: {len(post_links)}")
        for pl in post_links[:10]:
            print(f"    Text: '{await pl.inner_text()}', href='{await pl.get_attribute('href')}'")
    except Exception as e:
        print(f"  Error inspecting chovinh: {e}")

async def inspect_cvt_post(page):
    print("\n--- cvt.vn login status & post ---")
    try:
        await page.goto("https://cvt.vn/login/", wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(2000)
        await page.fill("#user_login", EMAIL)
        await page.fill("#user_pass", PASSWORD)
        await page.click("#wp-submit")
        await page.wait_for_timeout(5000)
        print(f"  URL after login click: {page.url}")
        await page.screenshot(path="detail_cvt_after_login.png")
        
        await page.goto("https://cvt.vn/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="detail_cvt_home_logged_in.png")
        
        post_links = await page.locator("a[href*='dangtin'], a[href*='dang-tin'], a[href*='create-thread']").all()
        print(f"  Post tin links found: {len(post_links)}")
        for pl in post_links[:10]:
            print(f"    Text: '{await pl.inner_text()}', href='{await pl.get_attribute('href')}'")
    except Exception as e:
        print(f"  Error inspecting cvt: {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        try:
            await inspect_chonhadat24h(page)
        except Exception as e:
            print(f"Error inspecting chonhadat24h: {e}")
            
        try:
            await inspect_nhaongay(page)
        except Exception as e:
            print(f"Error inspecting nhaongay: {e}")
            
        try:
            await inspect_nhadat_vn(page)
        except Exception as e:
            print(f"Error inspecting nhadat: {e}")
            
        try:
            await inspect_nhadatvn_com_vn(page)
        except Exception as e:
            print(f"Error inspecting nhadatvn: {e}")
            
        try:
            await inspect_vatgia(page)
        except Exception as e:
            print(f"Error inspecting vatgia: {e}")
            
        try:
            await inspect_chovinh_post(page)
        except Exception as e:
            print(f"Error inspecting chovinh: {e}")
            
        try:
            await inspect_cvt_post(page)
        except Exception as e:
            print(f"Error inspecting cvt: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
