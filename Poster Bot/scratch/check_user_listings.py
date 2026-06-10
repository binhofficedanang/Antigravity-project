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
        # Login
        bot.login_123nhadatviet(username, password)
        
        # Navigate to personal page
        # Usually it's /trang-ca-nhan.html or we can find the href from the "Quản lý cá nhân" link
        bot.page.goto("http://123nhadatviet.com/", wait_until="domcontentloaded")
        time.sleep(2)
        
        # Find href of "Quản lý cá nhân"
        manage_href = bot.page.evaluate("""() => {
            const el = Array.from(document.querySelectorAll('a')).find(a => a.innerText.includes('Quản lý cá nhân'));
            return el ? el.href : null;
        }""")
        print(f"Manage Href: {manage_href}")
        
        if manage_href:
            bot.page.goto(manage_href, wait_until="domcontentloaded")
            time.sleep(2)
            print(f"Personal Page URL: {bot.page.url}")
            
            # Print page title and first few listing titles if any
            bot.page.screenshot(path="personal_page.png")
            print("Captured personal page screenshot: personal_page.png")
            
            # Let's dump all text of table/list elements or anchor elements with listing class
            elements_text = bot.page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a')).map(a => a.innerText.trim()).filter(t => t.length > 10);
            }""")
            print("Listing links / texts found on page:")
            for text in elements_text[:30]:
                print(f"  - {text}")
        else:
            print("Could not find 'Quản lý cá nhân' link.")
            
    except Exception as e:
        print("Error:", e)
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
