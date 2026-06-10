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
    print("\n=== TESTING VATGIA.COM ===")
    await page.goto("https://www.vatgia.com/user/login", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    # Remove readonly attribute
    await page.evaluate("""() => {
        document.querySelectorAll('input[placeholder="Tên đăng nhập"]').forEach(el => el.removeAttribute('readonly'));
        document.querySelectorAll('input[placeholder="Mật khẩu"]').forEach(el => el.removeAttribute('readonly'));
    }""")
    
    # Fill fields
    await page.fill("input[placeholder='Tên đăng nhập']", EMAIL)
    await page.fill("input[placeholder='Mật khẩu']", PASSWORD)
    await page.screenshot(path="debug_vatgia_filled.png")
    
    # Click login button
    await page.click("button:has-text('Đăng nhập')")
    await page.wait_for_timeout(5000)
    
    print(f"  URL after login: {page.url}")
    await page.screenshot(path="debug_vatgia_after_login.png")

async def test_nhadatvn(page):
    print("\n=== TESTING NHADATVN.COM.VN ===")
    await page.goto("https://nhadatvn.com.vn/thanh-vien-khu-vuc-toan-quoc/dang-nhap/", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    # Force visibility in case fields are hidden in tab or modal
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
    
    # Fill inputs (using standard locator or via JS if still failing)
    try:
        await page.locator("input[name='sodienthoai']").fill(PHONE, timeout=5000)
        await page.locator("input[name='password']").fill(PASSWORD, timeout=5000)
    except Exception as e_fill:
        print(f"  Playwright fill failed, trying JS fill: {e_fill}")
        await page.evaluate(f"""() => {{
            document.querySelector("input[name='sodienthoai']").value = "{PHONE}";
            document.querySelector("input[name='password']").value = "{PASSWORD}";
        }}""")
        
    await page.screenshot(path="debug_nhadatvn_filled.png")
    
    # Click the login button in form
    btn_sel = "#login_feahfl button, #login_feahfl input[type='submit'], #login_feahfl input[type='button']"
    try:
        await page.locator(btn_sel).first.click(timeout=5000)
    except:
        await page.evaluate("""() => {
            const btn = document.querySelector("#login_feahfl button") || document.querySelector("#login_feahfl input[type='submit']");
            if (btn) btn.click();
        }""")
        
    await page.wait_for_timeout(5000)
    print(f"  URL after login: {page.url}")
    await page.screenshot(path="debug_nhadatvn_after_login.png")

async def test_chonhadat24h(page):
    print("\n=== TESTING CHONHADAT24H.COM ===")
    await page.goto("https://chonhadat24h.com/dang-nhap", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    # Find all text content of the page
    body_text = await page.inner_text("body")
    print(f"  Body text length: {len(body_text)}")
    print(f"  Is 'đăng nhập' in body? {'đăng nhập' in body_text.lower()}")
    
    # Check if there are any forms
    inputs = await page.locator("input").all()
    print(f"  Total inputs on dang-nhap: {len(inputs)}")
    for idx, inp in enumerate(inputs[:10]):
        print(f"    [{idx}] name='{await inp.get_attribute('name')}', type='{await inp.get_attribute('type')}', placeholder='{await inp.get_attribute('placeholder')}'")
        
    # Save a screenshot to inspect
    await page.screenshot(path="debug_chonhadat_dangnhap.png")

async def test_nhaongay(page):
    print("\n=== TESTING NHAONGAY.VN ===")
    await page.goto("https://nhaongay.vn/", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    # Try finding and clicking "Đăng nhập"
    found = False
    links = await page.locator("a, button, span, div").all()
    for idx, el in enumerate(links):
        try:
            text = await el.inner_text()
            tag = await el.evaluate("el => el.tagName")
            if "đăng nhập" in text.lower() and len(text.strip()) < 30:
                is_vis = await el.is_visible()
                print(f"    Element [{idx}] <{tag}>: text='{text.strip()}', visible={is_vis}")
                if is_vis:
                    print("    Clicking this element...")
                    await el.click()
                    await page.wait_for_timeout(4000)
                    await page.screenshot(path="debug_nhaongay_modal_open.png")
                    found = True
                    break
        except:
            pass
            
    if not found:
        # Try direct navigation to register/login or popup triggers
        print("    Could not click visible login button. Trying direct url.")
        await page.goto("https://nhaongay.vn/dang-nhap", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="debug_nhaongay_direct_dangnhap.png")

async def test_nhadat_vn(page):
    print("\n=== TESTING NHADAT.VN ===")
    await page.goto("https://nhadat.vn/", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    links = await page.locator("a").all()
    for l in links[:30]:
        href = await l.get_attribute("href") or ""
        text = await l.inner_text()
        if "rao vặt" in text.lower() or "raovat" in href.lower() or "login" in href.lower() or "dang-nhap" in href.lower():
            print(f"  Link: '{text.strip()}' -> '{href}'")
            
    # Try to load raovat.nhadat.vn directly
    print("  Loading http://raovat.nhadat.vn/")
    try:
        await page.goto("http://raovat.nhadat.vn/", wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(3000)
        print(f"    URL: {page.url}")
        print(f"    Title: {await page.title()}")
        await page.screenshot(path="debug_nhadat_raovat_home.png")
        
        # Check login links on raovat
        rv_links = await page.locator("a").all()
        for rl in rv_links[:40]:
            r_href = await rl.get_attribute("href") or ""
            r_text = await rl.inner_text()
            if "đăng nhập" in r_text.lower() or "login" in r_href.lower() or "dang-nhap" in r_href.lower():
                print(f"    Raovat Login Link: '{r_text.strip()}' -> '{r_href}'")
    except Exception as e:
        print(f"    Failed: {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        print("--- RUNNING VATGIA TEST ---")
        try:
            await test_vatgia(page)
        except Exception as e:
            print(f"VATGIA FAILED: {e}")
            
        print("--- RUNNING NHADATVN TEST ---")
        try:
            await test_nhadatvn(page)
        except Exception as e:
            print(f"NHADATVN FAILED: {e}")
            
        print("--- RUNNING CHONHADAT24H TEST ---")
        try:
            await test_chonhadat24h(page)
        except Exception as e:
            print(f"CHONHADAT24H FAILED: {e}")
            
        print("--- RUNNING NHAONGAY TEST ---")
        try:
            await test_nhaongay(page)
        except Exception as e:
            print(f"NHAONGAY FAILED: {e}")
            
        print("--- RUNNING NHADAT TEST ---")
        try:
            await test_nhadat_vn(page)
        except Exception as e:
            print(f"NHADAT FAILED: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
