"""
Script cào form bước 2 của raovat.net (sau khi chọn danh mục)
"""
import time
from playwright.sync_api import sync_playwright

EMAIL    = "binh.officedanang@gmail.com"
PASSWORD = "Binh1995@"
OUTPUT_FILE = "raovat_form_step2.html"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )
    page = context.new_page()

    # Bước 1: Đăng nhập
    print("=== Đăng nhập ===")
    page.goto("https://raovat.net/dang-nhap", wait_until="domcontentloaded")
    time.sleep(1)
    page.fill("input[name='useremail']", EMAIL)
    page.fill("input[name='password']", PASSWORD)
    page.click("button#buttonLogin")
    time.sleep(3)
    print(f"URL sau login: {page.url}")

    # Bước 2: Vào trang chọn danh mục
    print("=== Vào form đăng tin ===")
    page.goto("https://raovat.net/dang-tin-11-Nha-cua-Dat-dai", wait_until="domcontentloaded")
    time.sleep(2)
    print(f"URL form step1: {page.url}")

    # Bước 3: Chọn subcategory "Thuê và cho thuê nhà" (subcatid=51) bằng JS
    print("=== Chọn danh mục con: Thuê và cho thuê nhà (51) ===")
    page.evaluate("""
        () => {
            // Tìm div subcategory "Thuê và cho thuê nhà"
            const subDiv = document.querySelector('.sub-cate[onclick*="51"]');
            if (subDiv) {
                subDiv.click();
                console.log('Clicked subcategory 51');
            }
        }
    """)
    time.sleep(1)

    # Bước 4: Submit form step 1
    print("=== Submit step 1 ===")
    page.evaluate("""
        () => {
            // Set hidden fields
            document.querySelector('input[name="subcatid"]').value = '51';
            document.querySelector('input[name="sitecatid"]').value = '11';
            // Submit form
            document.getElementById('frmStep1').submit();
        }
    """)
    time.sleep(3)
    print(f"URL sau step 1: {page.url}")
    print(f"Title: {page.title()}")

    # Lưu HTML step 2
    html = page.content()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n✅ Đã lưu HTML step 2 vào: {OUTPUT_FILE}")

    # Phân tích các trường form step 2
    print("\n=== PHÂN TÍCH FORM STEP 2 ===")
    inputs = page.evaluate("""
        () => {
            const inputs = Array.from(document.querySelectorAll('input, textarea, select'));
            return inputs.map(el => ({
                tag: el.tagName,
                type: el.type || '',
                name: el.name || '',
                id: el.id || '',
                placeholder: el.placeholder || '',
                value: (el.value || '').substring(0, 30)
            })).filter(el => el.name || el.id);
        }
    """)
    
    for inp in inputs:
        print(f"  [{inp['tag']}] name='{inp['name']}' | id='{inp['id']}' | placeholder='{inp['placeholder'][:40]}' | value='{inp['value']}'")

    print("\n=== NÚT SUBMIT ===")
    buttons = page.evaluate("""
        () => Array.from(document.querySelectorAll('button,input[type=submit]')).map(el => ({
            id: el.id, text: (el.innerText||el.value||'').trim().substring(0,50), name: el.name||''
        }))
    """)
    for btn in buttons:
        print(f"  id='{btn['id']}' | text='{btn['text']}'")

    time.sleep(5)
    browser.close()
    print("\n=== XONG ===")
