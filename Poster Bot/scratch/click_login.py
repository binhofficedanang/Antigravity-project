#!/usr/bin/env python3
import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})
        
        try:
            print("Navigating to muaban.net...")
            page.goto("https://muaban.net/", timeout=30000)
            time.sleep(5)
            
            # Print all button and link text to find "Đăng nhập"
            print("Finding elements...")
            elements = page.evaluate("""
                () => {
                    const elList = [];
                    document.querySelectorAll('a, button, div').forEach(el => {
                        const text = el.innerText ? el.innerText.trim() : '';
                        if (text.includes('Đăng nhập') || text.includes('đăng nhập')) {
                            elList.push({
                                tagName: el.tagName,
                                className: el.className,
                                id: el.id,
                                text: text,
                                href: el.href || ''
                            });
                        }
                    });
                    return elList;
                }
            """)
            print(f"Found {len(elements)} potential login elements:")
            for idx, el in enumerate(elements[:15]):
                print(f"{idx}: <{el['tagName']} class='{el['className']}' id='{el['id']}' href='{el['href']}'>: '{el['text'][:50]}'")
                
            # Let's try to click the login element
            print("Clicking 'Đăng nhập'...")
            # Usually it has text "Đăng nhập" or a link with href/icon
            login_link = page.locator("text=Đăng nhập").first
            if login_link.count() > 0:
                print("Clicking using locator text=Đăng nhập...")
                login_link.click()
            else:
                print("Trying fallback selectors...")
                page.locator("a:has-text('Đăng nhập')").first.click()
                
            time.sleep(5)
            print(f"URL after click: {page.url}")
            page.screenshot(path="scratch/muaban_login_clicked.png")
            print("Saved muaban_login_clicked.png")
            with open("scratch/muaban_login_clicked.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("Saved muaban_login_clicked.html")
            
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="scratch/muaban_click_error.png")
            
        browser.close()

if __name__ == "__main__":
    main()
