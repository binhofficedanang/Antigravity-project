import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

bot = WebAutomation(headless=False)
try:
    bot.start()
    bot.login_dangtinbatdongsan("binhofficedanang", "Binh1995@")
    time.sleep(3)
    
    bot.page.goto("https://dangtinbatdongsan.vn/qttv/nhathue", wait_until="domcontentloaded")
    time.sleep(3)
    
    bot.page.click("#btnThem")
    time.sleep(2)
    
    # Define test data
    title = "Cho thuê văn phòng trống 600m2 cực đẹp ở tòa nhà DẦU KHÍ PVFC, Hải Châu"
    address = "Tòa nhà Dầu khí PVFC, Lô 10-B1.10, Đường 2 Tháng 9, Hải Châu, Đà Nẵng"
    area = "600"
    price = "150" # 150 Triệu đồng/tháng
    content = "Cho thuê văn phòng trống 600m2 cực đẹp ở tòa nhà DẦU KHÍ PVFC, Hải Châu.\n- Diện tích sử dụng: 600m2\n- Vị trí đắc địa, ngay trung tâm quận Hải Châu.\n- Liên hệ để biết thêm chi tiết!"
    
    # Fill using jQuery directly on the page to handle hidden/visible EasyUI elements
    bot.page.evaluate(f"""() => {{
        // Standard inputs
        $('#txtTen').val(`{title}`);
        $('#txtDiaChi').val(`{address}`);
        
        // CKEditor detailed description setting if available
        if (window.CKEDITOR && CKEDITOR.instances.txtMoTaChiTiet) {{
            CKEDITOR.instances.txtMoTaChiTiet.setData(`{content.replace('\n', '<br>')}`);
        }} else {{
            $('#txtMoTaChiTiet').val(`{content}`);
        }}
        
        // EasyUI Area field (hidden + visible input)
        $('#txtDienTich').val(`{area}`);
        $('#_easyui_textbox_input9').val(`{area}`);
        
        // EasyUI Price field (hidden + visible input)
        $('#txtGiaBan').val(`{price}`);
        $('#_easyui_textbox_input13').val(`{price}`);
        
        // EasyUI Combotrees
        $('#cboNhomNhaThue').combotree('setValue', '4'); // Cho thuê văn phòng
        $('#cboTTP').combotree('setValue', '48'); // Đà Nẵng
        $('#cboDonViGiaBan').combotree('setValue', '1000000'); // Triệu đồng
    }}""")
    
    time.sleep(3) # Wait for ward combo to load
    
    # Set ward/district
    bot.page.evaluate("() => $('#cboXa').combotree('setValue', '20242')") # Phường Hải Châu
    time.sleep(1)
    
    # Download and upload images
    local_images = bot.download_property_images("https://officedanang.vn/property/toa-nha-dau-khi-pvfc/", title)
    if local_images:
        print(f"Downloaded {len(local_images)} images. Uploading first single image...")
        file_input = bot.page.locator("input[type='file']")
        if file_input.count() > 0:
            try:
                # Upload single file
                file_input.first.set_input_files(local_images[0])
                time.sleep(3)
                print("✓ First image uploaded successfully.")
            except Exception as e:
                print(f"Error uploading image: {e}")
                
    bot.safe_screenshot("dangtin_js_filled.png")
    
    # Click Save
    print("Saving form...")
    bot.page.click("#btnLuu")
    time.sleep(5)
    
    bot.safe_screenshot("dangtin_js_submit_result.png")
    print(f"Final URL: {bot.page.url}")
    
finally:
    bot.stop()
