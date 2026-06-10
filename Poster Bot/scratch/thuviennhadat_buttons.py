import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print("Đang mở trang đăng nhập...")
        page.goto("https://thuviennhadat.vn/Users/Login?returnUrl=%2Fdang-tin", wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)
        
        buttons = page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('button')).map(btn => ({
                    id: btn.id,
                    className: btn.className,
                    innerText: btn.innerText.trim(),
                    visible: btn.offsetWidth > 0 && btn.offsetHeight > 0
                }));
            }
        """)
        
        print("\n=== DANH SÁCH BUTTONS TRÊN TRANG ===")
        for i, btn in enumerate(buttons):
            print(f"{i}. ID: '{btn['id']}' | Class: '{btn['className']}' | Text: '{btn['innerText']}' | Visible: {btn['visible']}")
            
        browser.close()

if __name__ == "__main__":
    main()
