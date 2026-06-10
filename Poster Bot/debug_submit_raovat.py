"""
Script kiểm tra kết quả submit đăng tin của raovat.net
"""
import time
from playwright.sync_api import sync_playwright

EMAIL    = "binh.officedanang@gmail.com"
PASSWORD = "Binh1995@"
OUTPUT_FILE = "raovat_submit_result.html"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )
    page = context.new_page()

    # 1. Login
    print("=== Đăng nhập ===")
    page.goto("https://raovat.net/dang-nhap", wait_until="domcontentloaded")
    time.sleep(1)
    page.fill("input[name='useremail']", EMAIL)
    page.fill("input[name='password']", PASSWORD)
    page.click("button#buttonLogin")
    time.sleep(3)

    # 2. Go to step 1
    page.goto("https://raovat.net/dang-tin-11-Nha-cua-Dat-dai", wait_until="domcontentloaded")
    time.sleep(2)

    # 3. Select category
    page.evaluate("""
        () => {
            const subDiv = document.querySelector('.sub-cate[onclick*="51"]');
            if (subDiv) subDiv.click();
            document.querySelector('input[name="subcatid"]').value = '51';
            document.querySelector('input[name="sitecatid"]').value = '11';
        }
    """)
    time.sleep(1)
    page.evaluate("document.getElementById('frmStep1').submit()")
    time.sleep(3)

    # 4. Fill step 2
    print("=== Điền form step 2 ===")
    
    # Tiêu đề (< 50 kí tự)
    title = "Cho thuê văn phòng xịn tại Hải Châu Đà Nẵng"
    page.fill("input[name='sitetitle']", title)

    # Chọn Loại tin (notify) = T (Thuê - Cho thuê)
    page.evaluate("document.querySelector('select[name=\"notify\"]').value = 'T';")
    
    # Chọn Thành phố (Đà Nẵng = value 4)
    print("- Chọn Tỉnh thành Đà Nẵng và kích hoạt AJAX...")
    page.evaluate("""
        () => {
            const citySel = document.querySelector('select[name="cityid"]');
            if (citySel) {
                citySel.value = '4';
                citySel.dispatchEvent(new Event('change', {bubbles: true}));
            }
        }
    """)
    
    # Đợi AJAX tải danh sách quận huyện (subcity)
    print("- Đợi danh sách quận huyện tải...")
    time.sleep(2)

    # Chọn Quận huyện (subcity) phù hợp từ CSV (ví dụ: Hải Châu)
    print("- Chọn Quận huyện (Hải Châu) từ danh sách...")
    page.evaluate("""
        () => {
            const subcitySel = document.querySelector('select[name="subcity"]');
            if (!subcitySel) return;
            
            // Tìm option chứa chữ "Hải Châu" hoặc "Hai Chau"
            const opt = Array.from(subcitySel.options).find(
                o => o.text.toLowerCase().includes('hải châu') || 
                     o.text.toLowerCase().includes('hai chau')
            );
            if (opt) {
                subcitySel.value = opt.value;
                subcitySel.dispatchEvent(new Event('change', {bubbles: true}));
                console.log('Set subcity to ' + opt.value + ' - ' + opt.text);
            } else {
                console.log('Không tìm thấy quận Hải Châu, các options hiện có: ' + 
                            Array.from(subcitySel.options).map(o => o.text).join(', '));
            }
        }
    """)
    time.sleep(1)

    # Điền giá
    page.evaluate("document.querySelector('input[name=\"siteprice\"]').value = '5000000';")
    page.evaluate("document.querySelector('select[name=\"sitecurrency\"]').value = '1';")
    page.evaluate("document.querySelector('input[name=\"siteunit\"]').value = 'tháng';")

    # Điền nội dung
    page.fill("textarea[name='sitedescription']", "Văn phòng cao cấp tại trung tâm Đà Nẵng, diện tích 50m2, đầy đủ tiện nghi. Liên hệ ngay!")

    # Điền từ khóa
    page.fill("input[name='sitetags']", "cho thue van phong, van phong da nang")

    # Đóng modal
    page.evaluate("""
        () => {
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
            document.querySelectorAll('.modal.in').forEach(el => el.remove());
            document.body.classList.remove('modal-open');
        }
    """)
    time.sleep(1)

    # Click Submit
    print("=== Submit Đăng tin ===")
    page.evaluate("""
        () => {
            const btn = document.querySelector('button.btn-success');
            if (btn) btn.click();
        }
    """)
    
    # Đợi 5 giây để load kết quả
    time.sleep(5)
    print(f"URL sau submit: {page.url}")
    print(f"Title sau submit: {page.title()}")

    # Chụp màn hình để debug trực quan!
    page.screenshot(path="raovat_debug_submit.png")
    print("📸 Đã chụp màn hình raovat_debug_submit.png")

    # Lấy thông báo lỗi nếu có trên trang mới
    errors = page.evaluate("""
        () => {
            const el = document.querySelector('.alert-danger, .error, .msg-error');
            return el ? el.innerText : 'Không tìm thấy class lỗi tiêu chuẩn';
        }
    """)
    print(f"Thông báo lỗi bằng selector: {errors}")

    # In ra toàn bộ text của body
    body_text = page.evaluate("document.body.innerText")
    print("\n=== TOÀN BỘ CHỮ TRÊN TRANG (300 ký tự đầu) ===")
    print(body_text[:500])

    # Lưu HTML
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(page.content())
    print(f"\n✅ Đã lưu HTML kết quả vào: {OUTPUT_FILE}")

    browser.close()
