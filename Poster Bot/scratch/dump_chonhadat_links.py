import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://chonhadat24h.com/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        links = await page.locator("a").all()
        print(f"Total links found: {len(links)}")
        for idx, l in enumerate(links):
            href = await l.get_attribute("href") or ""
            text = await l.inner_text()
            text = text.strip().replace("\n", " ")
            if text or href:
                print(f"  [{idx}] text='{text}' -> href='{href}'")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
