import pyautogui
import time
import os
import cv2
import numpy as np
import json
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGETS_DIR = os.path.join(BASE_DIR, 'targets')

# Kịch bản cày cuốc chính (34 bước - Bản ổn định 04/05)
SEQUENCE = [
    {"image": "active.png", "clicks": 1},
    {"image": "thuong.png", "clicks": 2},
    {"image": "tatcongtrinh.png", "clicks": 1},
    {"image": "quandoan.png", "clicks": 1},
    {"image": "baodanh.png", "clicks": 1},
    {"image": "nhan.png", "clicks": 1},
    {"image": "back.png", "clicks": 1},
    {"image": "trothu.png", "clicks": 1},
    {"image": "thuchientrothu.png", "clicks": 1},
    {"image": "tatcongtrinh.png", "clicks": 1},
    {"image": "backtrothu.png", "clicks": 1},
    {"image": "thanhchinh.png", "clicks": 1},
    {"image": "quocchinh1.png", "clicks": 1},
    {"image": "quocchinh2.png", "clicks": 1},
    {"image": "quockho.png", "clicks": 1},
    {"image": "tangvangquockho.png", "clicks": 1},
    {"image": "tickqk.png", "clicks": 1},
    {"image": "dongyqk.png", "clicks": 1},
    {"image": "tangvangquockho.png", "clicks": 49},
    {"image": "back.png", "clicks": 1},
    {"image": "thoat.png", "clicks": 1},
    {"image": "tatcongtrinh.png", "clicks": 1},
    {"image": "thegioimoi.png", "clicks": 1},
    {"image": "nhanthegioimoi.png", "clicks": 1},
    {"image": "nhan.png", "clicks": 1},
    {"image": "tatcongtrinh.png", "clicks": 1},
    {"image": "thanhchinhto.png", "clicks": 1},
    {"image": "nangdong.png", "clicks": 1},
    {"image": "nhannhanh.png", "clicks": 1},
    {"image": "ruongnangdong.png", "clicks": 1},
    {"image": "ruongnangdong.png", "clicks": 1},
    {"image": "ruongnangdong.png", "clicks": 1},
    {"image": "ruongnangdong.png", "clicks": 1},
    {"image": "diemdanh.png", "clicks": 1},
    {"image": "tatcongtrinh.png", "clicks": 1},
]

def locate_and_click_smart(image_path, clicks, threshold=0.65):
    try:
        screen_pil = pyautogui.screenshot()
        screen_width, screen_height = pyautogui.size()
        scale_factor = screen_pil.size[0] / screen_width
        
        screen_img = cv2.cvtColor(np.array(screen_pil), cv2.COLOR_RGB2BGR)
        template = cv2.imread(image_path)
        
        if template is None:
            return False
            
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
        
        best_match = None
        for scale in np.linspace(0.8, 1.2, 10):
            width = int(template_gray.shape[1] * scale)
            height = int(template_gray.shape[0] * scale)
            
            if width < 10 or height < 10 or height > screen_gray.shape[0] or width > screen_gray.shape[1]:
                continue
                
            resized = cv2.resize(template_gray, (width, height))
            result = cv2.matchTemplate(screen_gray, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                if best_match is None or max_val > best_match[0]:
                    best_match = (max_val, max_loc, width, height)
                    if max_val > 0.95:
                        break
                    
        if best_match:
            max_val, max_loc, width, height = best_match
            phys_x = max_loc[0] + width // 2
            phys_y = max_loc[1] + height // 2
            mouse_x = phys_x / scale_factor
            mouse_y = phys_y / scale_factor
            
            for _ in range(clicks):
                pyautogui.click(mouse_x, mouse_y)
                if clicks > 1:
                    time.sleep(0.05) 
            return True
            
        return False
    except Exception as e:
        print(f"Lỗi khi tìm ảnh: {e}")
        return False

def wait_and_click(image_name, clicks=1, max_wait=2.0, threshold=0.65):
    if not image_name.endswith('.png'):
        image_name += '.png'
        
    image_path = os.path.join(TARGETS_DIR, image_name)
    
    if not os.path.exists(image_path):
        print(f"Lỗi: Không tìm thấy file '{image_name}'. Bỏ qua.")
        return False
        
    print(f"Đang tìm ảnh '{image_name}' trên màn hình...")
    start_time = time.time()
    
    while True:
        if locate_and_click_smart(image_path, clicks, threshold):
            print(f" -> Đã click '{image_name}' {clicks} lần.")
            time.sleep(0.5) 
            return True
            
        if time.time() - start_time > max_wait:
            print(f" -> Cảnh báo: Bỏ qua '{image_name}'.")
            return False
            
        time.sleep(0.5)

def run_sequence():
    consecutive_skips = 0
    for idx, step in enumerate(SEQUENCE):
        print(f"\nBước {idx + 1}/{len(SEQUENCE)}:")
        success = wait_and_click(step["image"], step.get("clicks", 1))
        
        if success and "wait_after" in step:
            print(f" -> Đang chờ thêm {step['wait_after']} giây theo yêu cầu...")
            time.sleep(step["wait_after"])
            
        if not success:
            consecutive_skips += 1
            if consecutive_skips >= 3:
                print("\n[BÁO ĐỘNG] Trượt 3 hình liên tiếp! Dừng cày acc này.")
                return False
        else:
            consecutive_skips = 0
    return True

def login(account):
    print(f"\nĐang đăng nhập tài khoản: {account['username']}...")
    
    # 1. Chọn cách đăng nhập
    print("-> Đợi chọn phương thức đăng nhập...")
    wait_and_click("chon_cach_dang_nhap.png", 1, max_wait=15.0)
    time.sleep(1)
    
    # 2. Tìm ô nhập tài khoản và click vào
    print("-> Tìm ô nhập tài khoản...")
    success = wait_and_click("nhap_taikhoan.png", 1, max_wait=10.0)
    if not success:
        print("Không tìm thấy ô đăng nhập! Bỏ qua tài khoản này.")
        return False
        
    # 3. Gõ tài khoản
    time.sleep(0.5)
    pyautogui.write(account['username'], interval=0.05)
    
    # 4. Dùng phím TAB để nhảy sang ô mật khẩu
    print("-> Bấm phím Tab để nhảy sang ô Mật khẩu...")
    time.sleep(0.5)
    pyautogui.press('tab')
    
    # 5. Gõ mật khẩu
    time.sleep(0.5)
    pyautogui.write(account['password'], interval=0.05)
    
    # 6. Bấm nút đăng nhập
    print("-> Bấm Đăng nhập...")
    wait_and_click("dangnhap_btn.png", 1, max_wait=5.0)
    time.sleep(2)
    
    # 7. Chọn Server
    print("-> Đợi chọn Server...")
    wait_and_click("chon_server.png", 1, max_wait=15.0)
    
    print("Đang chờ 7 giây để game tải xong hoàn toàn...")
    time.sleep(7)
    return True

def logout():
    print("\nĐang quay lại trang đăng nhập (Thoát game)...")
    
    # Thử click hình Mũi tên lùi trang của trình duyệt trước
    success = wait_and_click("back_browser.png", 1, max_wait=3.0)
    if not success:
        print("-> Không thấy ảnh back_browser.png. Tự động lùi trang bằng phím tắt Mac...")
        pyautogui.hotkey('command', 'left')
        time.sleep(0.5)
        
    print("Đang chờ 8 giây để trang tải lại...")
    time.sleep(8)
    
    print("-> Tìm nút Thoát tài khoản Zing...")
    wait_and_click("thoat_zing.png", 1, max_wait=10.0)
    time.sleep(3)

if __name__ == "__main__":
    print("=== BOT NGỌA LONG MULTI-ACCOUNT ===")
    
    try:
        accounts_file = os.path.join(BASE_DIR, "accounts.json")
        with open(accounts_file, "r") as f:
            accounts = json.load(f)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {accounts_file}!")
        exit()
        
    start_acc = 1
    if len(sys.argv) > 1:
        try:
            start_acc = int(sys.argv[1])
            print(f"[*] Chế độ tuỳ chỉnh: BẮT ĐẦU TỪ TÀI KHOẢN SỐ {start_acc}")
        except ValueError:
            pass
            
    print("Mẹo: Kéo chuột vào góc màn hình để dừng bot khẩn cấp!")
    print("Bot sẽ bắt đầu sau 3 giây...")
    time.sleep(3)
    
    for idx, acc in enumerate(accounts):
        acc_num = idx + 1
        if acc_num < start_acc:
            continue
            
        print(f"\n=====================================")
        print(f"BẮT ĐẦU TÀI KHOẢN {acc_num}/{len(accounts)}: {acc['username']}")
        print(f"=====================================")
        
        if login(acc):
            run_sequence()
            
        logout()
        
    print("\n=== ĐÃ CÀY XONG TẤT CẢ TÀI KHOẢN ===")
