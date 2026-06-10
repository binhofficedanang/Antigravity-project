#!/usr/bin/env python3
import time
import json
from playwright.sync_api import sync_playwright

def main():
    print("Interactive script to scan muaban.net final form...")
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    acc = config.get("muaban.net", {})
    username = acc.get("username")
    password = acc.get("password")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context()
        page = context.new_page()
        
        try:
            page.goto("https://muaban.net/")
            time.sleep(3)
            
            # Login
            login_btn = page.locator("text=Đăng nhập").first
            if login_btn.count() > 0:
                login_btn.click()
                time.sleep(2)
                page.fill("input[name='phone'], input[type='tel']", username)
                page.fill("input[name='password'], input[type='password']", password)
                submit_btn = page.locator("button.iyHKgc, button:has-text('Đăng nhập')").last
                submit_btn.click()
                time.sleep(5)
            
            page.goto("https://muaban.net/dang-tin")
            print("Please select the category manually in the visible browser within the next 30 seconds...")
            time.sleep(30)
            
            # Scan form
            print("Scanning inputs on the final form...")
            inputs = page.evaluate("""
                () => {
                    const inpList = [];
                    document.querySelectorAll('input, textarea, select, label').forEach(el => {
                        inpList.push({
                            tagName: el.tagName,
                            type: el.type || '',
                            name: el.name || '',
                            id: el.id || '',
                            placeholder: el.placeholder || '',
                            className: el.className || '',
                            text: el.innerText ? el.innerText.trim() : ''
                        });
                    });
                    return inpList;
                }
            """)
            print(f"Found {len(inputs)} form elements:")
            for idx, el in enumerate(inputs):
                text_str = f"text='{el['text'][:30]}'" if el['text'] else ""
                print(f"{idx}: <{el['tagName']} type='{el['type']}' name='{el['name']}' placeholder='{el['placeholder']}' class='{el['className']}' {text_str}>")
                
            page.screenshot(path="scratch/muaban_final_form_interactive.png")
            print("Saved scratch/muaban_final_form_interactive.png")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
