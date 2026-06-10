import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        # 1. dangtinbatdongsan.vn links
        print("\n--- Links on dangtinbatdongsan.vn ---")
        try:
            page.goto("https://dangtinbatdongsan.vn/", wait_until="domcontentloaded")
            time.sleep(2)
            links = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a')).map(a => ({
                    text: a.innerText.trim(),
                    href: a.getAttribute('href') || ''
                }));
            }""")
            for l in links:
                if any(k in l['text'].lower() or k in l['href'].lower() for k in ["nhap", "ky", "tin", "login", "post"]):
                    print(f"  Link: text='{l['text']}', href='{l['href']}'")
        except Exception as e:
            print("  Failed:", e)
            
        # 2. luachonnhadat.vn ALL form elements
        print("\n--- luachonnhadat.vn ALL form elements ---")
        try:
            page.goto("https://luachonnhadat.vn/dang-tin.html", wait_until="domcontentloaded")
            time.sleep(2)
            elements = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('input, textarea, select, button, label')).map(el => ({
                    tag: el.tagName,
                    id: el.getAttribute('id') || '',
                    name: el.getAttribute('name') || '',
                    type: el.getAttribute('type') || '',
                    text: el.innerText || '',
                    placeholder: el.getAttribute('placeholder') || ''
                }));
            }""")
            for idx, el in enumerate(elements):
                if el['tag'] in ['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON'] or any(k in el['text'].lower() for k in ["tiêu đề", "mô tả", "giá", "diện tích", "địa chỉ"]):
                    print(f"  [{idx}] {el['tag']}: id='{el['id']}', name='{el['name']}', placeholder='{el['placeholder']}', text='{el['text']}'")
        except Exception as e:
            print("  Failed:", e)
            
        # 3. diaocanphu.com ALL form elements
        print("\n--- diaocanphu.com ALL form elements ---")
        try:
            page.goto("http://diaocanphu.com/dang-tin.html", wait_until="domcontentloaded")
            time.sleep(2)
            elements = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('input, textarea, select, button')).map(el => ({
                    tag: el.tagName,
                    id: el.getAttribute('id') || '',
                    name: el.getAttribute('name') || '',
                    type: el.getAttribute('type') || '',
                    placeholder: el.getAttribute('placeholder') || ''
                }));
            }""")
            for idx, el in enumerate(elements):
                print(f"  [{idx}] {el['tag']}: id='{el['id']}', name='{el['name']}', type='{el['type']}', placeholder='{el['placeholder']}'")
        except Exception as e:
            print("  Failed:", e)
            
        browser.close()

if __name__ == '__main__':
    inspect()
