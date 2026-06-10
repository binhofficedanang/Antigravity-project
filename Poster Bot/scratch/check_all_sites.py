"""Kiểm tra nhanh trạng thái tất cả các site"""
import asyncio
from playwright.async_api import async_playwright

SITES = {
    "rongbay.com":         "https://rongbay.com/",
    "muabandanang.vn":     "https://muabandanang.vn/",
    "nhachothue.vn":       "https://nhachothue.vn/",
    "datviet24h.com.vn":   "https://datviet24h.com.vn/dang-nhap.html",
    "raovat247.net":       "https://raovat247.net/",
    "nhadat24h.net":       "https://nhadat24h.net/",
    "timkiemnhadat.vn":    "https://timkiemnhadat.vn/",
}

async def check(name, url):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        try:
            r = await page.goto(url, timeout=12000)
            status = r.status if r else "?"
            title = await page.title()
            final_url = page.url
            print(f"  [{status}] {name:25s} | {title[:45]}")
            if final_url != url:
                print(f"         => redirect: {final_url}")
        except Exception as e:
            err = str(e)[:70]
            print(f"  [ERR] {name:25s} | {err}")
        finally:
            await b.close()

async def main():
    print("\n=== Kiểm tra trạng thái site ===")
    tasks = [check(n, u) for n, u in SITES.items()]
    await asyncio.gather(*tasks)

asyncio.run(main())
