import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def explore_chonhadat(page):
    print("\n================= EXPLORING chonhadat24h.com =================")
    await page.goto("https://chonhadat24h.com/", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    # Let's find all links containing "nhập" or "login" or "đăng"
    links = await page.locator("a").all()
    print(f"Total links: {len(links)}")
    for l in links[:50]:
        text = await l.inner_text()
        href = await l.get_attribute("href") or ""
        if any(w in text.lower() or w in href.lower() for w in ["nhap", "login", "dang", "thanh-vien", "user"]):
            print(f"  Link: '{text.strip()}' -> '{href}'")
            
    # Go directly to login
    await page.goto("https://chonhadat24h.com/dang-nhap", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    # Save HTML
    html = await page.content()
    with open("chonhadat_login.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved chonhadat_login.html")

async def explore_nhaongay(page):
    print("\n================= EXPLORING nhaongay.vn =================")
    await page.goto("https://nhaongay.vn/", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    # Dump all links with "Đăng nhập" or "Đăng ký"
    links = await page.locator("a").all()
    for l in links:
        text = await l.inner_text()
        href = await l.get_attribute("href") or ""
        if "đăng nhập" in text.lower() or "đăng ký" in text.lower() or "login" in href.lower() or "register" in href.lower():
            print(f"  Link: '{text.strip()}' -> '{href}'")
            
    # Click on the login link to see what happens
    login_link = page.locator("a:has-text('Đăng nhập')").first
    if await login_link.count() > 0:
        await login_link.click()
        await page.wait_for_timeout(3000)
        html = await page.content()
        with open("nhaongay_login_modal.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Clicked login link and saved nhaongay_login_modal.html")

async def explore_nhadat_vn(page):
    print("\n================= EXPLORING nhadat.vn =================")
    await page.goto("https://nhadat.vn/", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    links = await page.locator("a").all()
    for l in links[:60]:
        text = await l.inner_text()
        href = await l.get_attribute("href") or ""
        if any(w in text.lower() or w in href.lower() for w in ["nhap", "login", "dang", "thanh-vien"]):
            print(f"  Link: '{text.strip()}' -> '{href}'")
            
    # Let's save homepage HTML to see if there's any script or iframe
    html = await page.content()
    with open("nhadat_home.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved nhadat_home.html")

async def explore_nhadatvn_com_vn(page):
    print("\n================= EXPLORING nhadatvn.com.vn =================")
    await page.goto("https://nhadatvn.com.vn/thanh-vien-khu-vuc-toan-quoc/dang-nhap/", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    html = await page.content()
    with open("nhadatvn_login.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved nhadatvn_login.html")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        await explore_chonhadat(page)
        await explore_nhaongay(page)
        await explore_nhadat_vn(page)
        await explore_nhadatvn_com_vn(page)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
