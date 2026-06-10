import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_automation import WebAutomation

def main():
    bot = WebAutomation(headless=True)
    bot.start()
    
    username = "binhofficedanang"
    password = "Binh1995@"
    
    try:
        login_ok = bot.login_123nhadatviet(username, password)
        print(f"Login success: {login_ok}")
        
        # We are on home page, let's find the link that has text 'Quản lý cá nhân'
        personal_link = bot.page.locator("a:has-text('Quản lý cá nhân'), a:has-text('Trang cá nhân')").first
        if personal_link.count() > 0:
            print("Found personal link, clicking...")
            personal_link.click()
            time.sleep(3)
        else:
            print("Personal link not found, trying navigation to dashboard directly...")
            bot.page.goto("http://123nhadatviet.com/ca-nhan.html", wait_until="domcontentloaded")
            time.sleep(3)
            
        print(f"Current URL: {bot.page.url}")
        print(f"Page Title: {bot.page.title()}")
        
        # Save screenshot
        bot.page.screenshot(path="personal_page.png", full_page=True)
        print("Saved screenshot to personal_page.png")
        
        # Let's see if there are links for listings
        links = bot.page.locator("a").all()
        print(f"Total links on personal page: {len(links)}")
        for idx, link in enumerate(links[:50]):
            try:
                href = link.get_attribute("href")
                text = link.inner_text().strip()
                if href and ("tin" in href or "quan-ly" in href or "ca-nhan" in href):
                    print(f"  [{idx}] text='{text}', href='{href}'")
            except:
                pass
                
    except Exception as e:
        print("Error:", e)
    finally:
        bot.stop()

if __name__ == '__main__':
    main()
