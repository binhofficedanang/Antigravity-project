import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to https://www.maumau.vn/ ...")
        page.goto("https://www.maumau.vn/", wait_until="networkidle")
        time.sleep(3)
        
        print("Page URL:", page.url)
        print("Page Title:", page.title())
        
        # Save screenshot
        page.screenshot(path="scratch/maumau_home.png", full_page=True)
        print("Saved home screenshot to scratch/maumau_home.png")
        
        # Find all buttons/links
        links = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a, button')).map(el => ({
                tag: el.tagName,
                text: el.innerText.trim(),
                href: el.getAttribute('href') || ''
            })).filter(x => x.text.length > 0 || x.href.length > 0);
        }""")
        
        print(f"Found {len(links)} interactive elements:")
        for idx, l in enumerate(links[:50]):
            print(f"  [{idx}] {l['tag']}: text='{l['text']}', href='{l['href']}'")
            
        browser.close()

if __name__ == '__main__':
    inspect()
