import time
from playwright.sync_api import sync_playwright

def discover():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        url = "https://www.maumau.vn/"
        print(f"Navigating to {url} ...")
        page.goto(url, wait_until="networkidle")
        time.sleep(3)
        
        print("Page URL:", page.url)
        print("Page Title:", page.title())
        
        # Save screenshot
        page.screenshot(path="scratch/maumau_home_discover.png", full_page=True)
        print("Saved home screenshot to scratch/maumau_home_discover.png")
        
        # Find links containing "dang-tin", "post", "dang-nhap", or text like "Đăng tin"
        links = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a')).map(el => ({
                text: el.innerText.trim(),
                href: el.getAttribute('href') || ''
            }));
        }""")
        
        print(f"Found {len(links)} link elements:")
        for idx, link in enumerate(links):
            if any(k in link['text'].lower() or k in link['href'].lower() for k in ["tin", "post", "dang"]):
                print(f"  [{idx}] Text: '{link['text']}', Href: '{link['href']}'")
                
        browser.close()

if __name__ == '__main__':
    discover()
