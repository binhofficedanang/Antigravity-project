"""Tìm đúng URL và DOM của chothuenha + nhachothue"""
import asyncio
from playwright.async_api import async_playwright
import time

async def check_chothuenha():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            # Thử login chothuenha trước để tìm đúng trang đăng tin
            await page.goto("https://chothuenha.com.vn/dang-nhap", timeout=20000)
            print(f"\n[chothuenha.com.vn] Login page: {page.url}")
            inputs = await page.locator("input").all()
            for inp in inputs[:10]:
                t = await inp.get_attribute("type") or "text"
                n = await inp.get_attribute("name") or ""
                pid = await inp.get_attribute("id") or ""
                ph = await inp.get_attribute("placeholder") or ""
                print(f"  INPUT: type={t} name={n} id={pid} ph={ph}")
            
            # Điền đăng nhập
            try:
                await page.fill("input[name='Phone']", "0935723727")
                await page.fill("input[name='Password']", "Binh1995@")
                await page.click("button[type='submit'], button:has-text('Đăng nhập')")
                await page.wait_for_timeout(5000)
                print(f"  URL sau login: {page.url}")
            except Exception as e:
                print(f"  Login error: {e}")
            
            # Tìm URL đăng tin
            for url in ["https://chothuenha.com.vn/tao-bai-viet", 
                        "https://chothuenha.com.vn/dang-tin",
                        "https://chothuenha.com.vn/tai-khoan/dang-tin",
                        "https://chothuenha.com.vn/them-tin"]:
                try:
                    r = await page.goto(url, timeout=8000)
                    st = r.status if r else "?"
                    title = await page.title()
                    print(f"  URL test: {url} -> {st} | {title}")
                    inputs = await page.locator("input[type='text'], input[type='email']").all()
                    for inp in inputs[:3]:
                        n = await inp.get_attribute("name") or ""
                        pid = await inp.get_attribute("id") or ""
                        print(f"    INPUT: name={n} id={pid}")
                except Exception as e:
                    print(f"  URL test: {url} -> Error: {e}")
        finally:
            await browser.close()

async def check_nhachothue():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            # nhachothue.vn - login dạng modal trên homepage
            await page.goto("https://nhachothue.vn/", timeout=20000)
            print(f"\n[nhachothue.vn] Homepage: {page.url} | Title: {await page.title()}")
            
            # Fill login form
            try:
                await page.fill("#email-login", "binh.officedanang@gmail.com")
                await page.fill("#password-login", "Binh1995@")
                # Tìm nút submit login
                btns = await page.locator("button").all()
                for btn in btns[:10]:
                    txt = await btn.inner_text()
                    pid = await btn.get_attribute("id") or ""
                    cls = await btn.get_attribute("class") or ""
                    print(f"  BUTTON: text='{txt.strip()}' id={pid} class={cls}")
            except Exception as e:
                print(f"  Fill error: {e}")
            
            # Tìm URL đăng tin
            for url in ["https://nhachothue.vn/dang-tin", 
                        "https://nhachothue.vn/dang-tin.html",
                        "https://nhachothue.vn/create-post",
                        "https://nhachothue.vn/tao-tin"]:
                try:
                    r = await page.goto(url, timeout=8000)
                    st = r.status if r else "?"
                    title = await page.title()
                    print(f"  URL test: {url} -> {st} | {title}")
                except Exception as e:
                    print(f"  URL test: {url} -> Error: {str(e)[:80]}")
        finally:
            await browser.close()

async def main():
    await check_chothuenha()
    await check_nhachothue()

asyncio.run(main())
