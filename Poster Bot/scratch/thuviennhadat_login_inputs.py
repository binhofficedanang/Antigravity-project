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
        
        # Lấy danh sách inputs
        inputs = page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('input')).map(input => ({
                    id: input.id,
                    name: input.name,
                    type: input.type,
                    placeholder: input.placeholder,
                    visible: input.offsetWidth > 0 && input.offsetHeight > 0
                }));
            }
        """)
        
        print("\n=== DANH SÁCH INPUTS BAN ĐẦU ===")
        for i, inp in enumerate(inputs):
            print(f"{i}. ID: '{inp['id']}' | Name: '{inp['name']}' | Type: '{inp['type']}' | Visible: {inp['visible']} | Placeholder: '{inp['placeholder']}'")
            
        browser.close()

if __name__ == "__main__":
    main()
