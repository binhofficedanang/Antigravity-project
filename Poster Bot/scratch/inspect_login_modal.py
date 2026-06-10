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
            
            print("Opening login modal...")
            page.locator("text=Đăng nhập").first.click()
            time.sleep(3)
            
            # Print all input elements, their placeholder, and names
            print("Inspecting inputs...")
            inputs = page.evaluate("""
                () => {
                    const inpList = [];
                    document.querySelectorAll('input').forEach(el => {
                        inpList.push({
                            tagName: el.tagName,
                            type: el.type,
                            name: el.name,
                            placeholder: el.placeholder,
                            className: el.className,
                            id: el.id
                        });
                    });
                    return inpList;
                }
            """)
            print(f"Found {len(inputs)} input elements:")
            for idx, el in enumerate(inputs):
                print(f"{idx}: <{el['tagName']} type='{el['type']}' name='{el['name']}' placeholder='{el['placeholder']}' class='{el['className']}' id='{el['id']}'>")
                
            # Inspect buttons
            print("Inspecting buttons...")
            buttons = page.evaluate("""
                () => {
                    const btnList = [];
                    document.querySelectorAll('button, div[role="button"], a.btn').forEach(el => {
                        btnList.push({
                            tagName: el.tagName,
                            text: el.innerText ? el.innerText.trim() : '',
                            className: el.className,
                            id: el.id
                        });
                    });
                    return btnList;
                }
            """)
            print(f"Found {len(buttons)} button elements:")
            for idx, el in enumerate(buttons):
                if el['text']:
                    print(f"{idx}: <{el['tagName']} class='{el['className']}' id='{el['id']}'>: '{el['text'][:50]}'")
            
        except Exception as e:
            print(f"Error: {e}")
            
        browser.close()

if __name__ == "__main__":
    main()
