import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        # 1. datviet24h.com.vn
        print("\n--- Inspecting datviet24h.com.vn ---")
        try:
            page.goto("https://datviet24h.com.vn/", wait_until="domcontentloaded")
            time.sleep(2)
            links = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a')).map(a => ({
                    text: a.innerText.trim(),
                    href: a.getAttribute('href') || ''
                }));
            }""")
            for l in links:
                if "nhập" in l['text'].lower() or "login" in l['href'].lower() or "dang-nhap" in l['href'].lower():
                    print(f"  Found login link: text='{l['text']}', href='{l['href']}'")
        except Exception as e:
            print("  Failed:", e)
            
        # 2. luachonnhadat.vn post form elements
        print("\n--- Inspecting luachonnhadat.vn post form ---")
        try:
            page.goto("https://luachonnhadat.vn/dang-tin.html", wait_until="domcontentloaded")
            time.sleep(2)
            inputs = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('input, textarea, select')).map(el => ({
                    tag: el.tagName,
                    id: el.getAttribute('id') || '',
                    name: el.getAttribute('name') || '',
                    placeholder: el.getAttribute('placeholder') || ''
                }));
            }""")
            print("  Inputs found on luachonnhadat.vn/dang-tin.html:")
            for inp in inputs[:15]:
                print(f"    {inp['tag']}: id='{inp['id']}', name='{inp['name']}', placeholder='{inp['placeholder']}'")
        except Exception as e:
            print("  Failed:", e)
            
        # 3. dangtinbatdongsan.vn login
        print("\n--- Inspecting dangtinbatdongsan.vn login ---")
        try:
            page.goto("http://dangtinbatdongsan.vn/", wait_until="domcontentloaded")
            time.sleep(2)
            links = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a')).map(a => ({
                    text: a.innerText.trim(),
                    href: a.getAttribute('href') || ''
                }));
            }""")
            for l in links:
                if "nhập" in l['text'].lower() or "login" in l['href'].lower() or "dang-nhap" in l['href'].lower():
                    print(f"  Found login link: text='{l['text']}', href='{l['href']}'")
        except Exception as e:
            print("  Failed:", e)
            
        # 4. diaocanphu.com login
        print("\n--- Inspecting diaocanphu.com login ---")
        try:
            page.goto("http://diaocanphu.com/", wait_until="domcontentloaded")
            time.sleep(2)
            links = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a')).map(a => ({
                    text: a.innerText.trim(),
                    href: a.getAttribute('href') || ''
                }));
            }""")
            for l in links:
                if "nhập" in l['text'].lower() or "login" in l['href'].lower() or "dang-nhap" in l['href'].lower():
                    print(f"  Found login link: text='{l['text']}', href='{l['href']}'")
        except Exception as e:
            print("  Failed:", e)
            
        browser.close()

if __name__ == '__main__':
    inspect()
