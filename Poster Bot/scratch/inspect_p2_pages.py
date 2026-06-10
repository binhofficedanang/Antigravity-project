import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # 1. raovatdanang.vn
        try:
            print("=== Visiting raovatdanang.vn ===")
            page.goto("https://raovatdanang.vn/", timeout=30000)
            page.wait_for_timeout(3000)
            links = page.evaluate("""() => {
                const results = [];
                document.querySelectorAll('a').forEach(a => {
                    results.push({text: a.innerText, href: a.href});
                });
                return results;
            }""")
            for l in links:
                t = l['text'].strip()
                h = l['href']
                if any(w in t.lower() or w in h.lower() for w in ["đăng", "tin", "nhập", "ký", "post", "login", "register", "account"]):
                    print(f"raovatdanang.vn link: {t} -> {h}")
        except Exception as e:
            print("Failed to visit raovatdanang.vn:", e)
            
        # 2. chodanang.com
        try:
            print("\n=== Visiting chodanang.com ===")
            page.goto("http://chodanang.com/", timeout=30000)
            page.wait_for_timeout(3000)
            links = page.evaluate("""() => {
                const results = [];
                document.querySelectorAll('a').forEach(a => {
                    results.push({text: a.innerText, href: a.href});
                });
                return results;
            }""")
            for l in links:
                t = l['text'].strip()
                h = l['href']
                if any(w in t.lower() or w in h.lower() for w in ["đăng", "tin", "nhập", "ký", "post", "login", "register", "account"]):
                    print(f"chodanang.com link: {t} -> {h}")
        except Exception as e:
            print("Failed to visit chodanang.com:", e)
            
        browser.close()

if __name__ == "__main__":
    inspect()
