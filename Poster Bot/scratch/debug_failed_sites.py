"""Script nhanh để kiểm tra DOM của các site lỗi"""
import asyncio
from playwright.async_api import async_playwright
import time

async def check_site(url, name):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            r = await page.goto(url, timeout=15000)
            print(f"\n[{name}] Status: {r.status} | URL: {page.url}")
            # Lấy title
            title = await page.title()
            print(f"  Title: {title}")
            # Kiểm tra form đăng nhập
            inputs = await page.locator("input").all()
            for inp in inputs[:5]:
                try:
                    t = await inp.get_attribute("type") or "text"
                    n = await inp.get_attribute("name") or ""
                    pid = await inp.get_attribute("id") or ""
                    ph = await inp.get_attribute("placeholder") or ""
                    print(f"  INPUT: type={t} name={n} id={pid} placeholder={ph}")
                except:
                    pass
        except Exception as e:
            print(f"[{name}] Error: {e}")
        finally:
            await browser.close()

async def main():
    sites = [
        ("https://timkiemnhadat.vn/dang-nhap", "timkiemnhadat.vn"),
        ("https://datviet24h.com.vn/dang-nhap.html", "datviet24h.com.vn"),
        ("https://nhachothue.vn/", "nhachothue.vn"),
        ("http://nhachothue.vn/", "nhachothue.vn (HTTP)"),
        ("https://chothuenha.com.vn/quan-ly/dang-tin-moi", "chothuenha.com.vn post"),
    ]
    for url, name in sites:
        await check_site(url, name)

asyncio.run(main())
