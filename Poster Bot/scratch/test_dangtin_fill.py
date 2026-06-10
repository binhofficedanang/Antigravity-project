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
    
    # Fill Title
    bot.page.fill("#txtTieuDe", "Cho thuê văn phòng trống 600m2 cực đẹp ở tòa nhà DẦU KHÍ PVFC")
    
    # Nhóm nhà thuê (Visible Element 23: #_easyui_textbox_input8)
    bot.page.click("#_easyui_textbox_input8")
    time.sleep(0.5)
    # Type and choose the option or just type
    bot.page.fill("#_easyui_textbox_input8", "Văn phòng")
    time.sleep(1)
    # Press ArrowDown and Enter to select
    bot.page.keyboard.press("ArrowDown")
    bot.page.keyboard.press("Enter")
    
    # Tỉnh/thành phố (Visible Element 26: #_easyui_textbox_input6)
    bot.page.click("#_easyui_textbox_input6")
    time.sleep(0.5)
    bot.page.fill("#_easyui_textbox_input6", "Đà Nẵng")
    time.sleep(1)
    bot.page.keyboard.press("ArrowDown")
    bot.page.keyboard.press("Enter")
    time.sleep(2) # wait for ward/district to load
    
    # Xã/phường (Visible Element 29: #_easyui_textbox_input7)
    bot.page.click("#_easyui_textbox_input7")
    time.sleep(0.5)
    bot.page.fill("#_easyui_textbox_input7", "Hải Châu")
    time.sleep(1)
    bot.page.keyboard.press("ArrowDown")
    bot.page.keyboard.press("Enter")
    
    # Dia Chi
    bot.page.fill("#txtDiaChi", "Tòa nhà Dầu khí PVFC, Hải Châu, Đà Nẵng")
    
    # Dien Tich
    bot.page.fill("#txtDienTich", "600")
    
    # Gia ban / Gia thue
    bot.page.fill("#txtGiaBan", "15")
    # Unit (Unit is default to Tỷ đồng, let's type Triệu đồng/tháng if needed)
    # Visible Element 49: #_easyui_textbox_input14 (Unit for Giá thuê)
    bot.page.click("#_easyui_textbox_input14")
    time.sleep(0.5)
    bot.page.fill("#_easyui_textbox_input14", "Triệu đồng/tháng")
    time.sleep(0.5)
    bot.page.keyboard.press("ArrowDown")
    bot.page.keyboard.press("Enter")
    
    # Mo ta chi tiet
    bot.page.fill("#txtMoTaChiTiet", "Cho thuê văn phòng trống 600m2 cực đẹp ở tòa nhà DẦU KHÍ PVFC. Liên hệ ngay!")
    
    bot.safe_screenshot("dangtin_form_filled_test.png")
    
finally:
    bot.stop()
