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
        
        # Lấy tất cả thẻ a
        links = page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('a')).map(a => ({
                    text: a.innerText.trim(),
                    href: a.href,
                    id: a.id,
                    className: a.className
                }));
            }
        """)
        
        print("\n=== DANH SÁCH LIÊN KẾT TRÊN TRANG ===")
        for i, link in enumerate(links):
            if link['text'] or link['href']:
                print(f"{i}. Text: '{link['text']}' | Href: '{link['href']}' | ID: '{link['id']}' | Class: '{link['className']}'")
        
        # Chụp màn hình trang đăng nhập để xem tại sao không click được
        page.screenshot(path="thuviennhadat_login_page.png")
        print("\nĐã chụp màn hình trang login vào thuviennhadat_login_page.png")
        
        browser.close()

if __name__ == "__main__":
    main()
