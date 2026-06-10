import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.vatgia.com/raovat/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        links = await page.locator("a").all()
        print(f"Total links: {len(links)}")
        for idx, l in enumerate(links):
            text = await l.inner_text()
            href = await l.get_attribute("href") or ""
            text = text.strip().replace("\n", " ")
            if text or href:
                print(f"  [{idx}] text='{text}' -> href='{href}'")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
