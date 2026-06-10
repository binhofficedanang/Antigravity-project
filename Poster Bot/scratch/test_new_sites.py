import os
import sys
import json
import csv
import time

# Thêm thư mục cha vào sys.path để import WebAutomation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_automation import WebAutomation

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_first_item():
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data.csv")
    if not os.path.exists(csv_path):
        print("Không tìm thấy data.csv")
        return None
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            return row
    return None

def test_site(site_key, bot, item, config):
    print(f"\n=========================================")
    print(f"BẮT ĐẦU KIỂM TRA TRANG: {site_key.upper()}")
    print(f"=========================================")
    
    acc = config.get(site_key, {})
    username = acc.get("username") or acc.get("email")
    password = acc.get("password")
    
    if not username or not password:
        print(f"❌ Chưa cấu hình thông tin tài khoản cho {site_key} trong config.json")
        return False

    try:
        # 1. Đăng nhập
        login_ok = False
        if site_key == "maumau.vn":
            login_ok = bot.login_maumau(username, password)
        elif site_key == "datviet24h.com.vn":
            login_ok = bot.login_datviet24h(username, password)
        elif site_key == "luachonnhadat.vn":
            print("luachonnhadat.vn sử dụng cơ chế đăng nhập trực tiếp qua Email khi đăng tin.")
            login_ok = True
        elif site_key == "dangtinbatdongsan.vn":
            login_ok = bot.login_dangtinbatdongsan(username, password)
        elif site_key == "diaocanphu.com":
            login_ok = bot.login_diaocanphu(username, password)
            
        if not login_ok:
            print(f"❌ Đăng nhập {site_key} thất bại.")
            return False
            
        print(f"✓ Đăng nhập {site_key} thành công / Sẵn sàng!")
        
        # 2. Đăng tin
        post_ok = False
        if site_key == "maumau.vn":
            post_ok = bot.post_maumau(item)
        elif site_key == "datviet24h.com.vn":
            post_ok = bot.post_datviet24h(item)
        elif site_key == "luachonnhadat.vn":
            post_ok = bot.post_luachonnhadat(item)
        elif site_key == "dangtinbatdongsan.vn":
            post_ok = bot.post_dangtinbatdongsan(item)
        elif site_key == "diaocanphu.com":
            post_ok = bot.post_diaocanphu(item)
            
        if post_ok:
            print(f"🎉 Đăng tin {site_key} THÀNH CÔNG!")
            return True
        else:
            print(f"❌ Đăng tin {site_key} THẤT BẠI!")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi trong quá trình kiểm tra {site_key}: {e}")
        return False

def main():
    config = load_config()
    item = load_first_item()
    if not item:
        print("Không có dữ liệu tin đăng trong data.csv.")
        return
        
    print(f"Tin đăng thử nghiệm: {item.get('title')}")
    
    # Lấy tham số dòng lệnh để chạy riêng từng trang hoặc tất cả
    target_site = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    sites_to_test = ["maumau.vn", "datviet24h.com.vn", "luachonnhadat.vn", "dangtinbatdongsan.vn", "diaocanphu.com"]
    if target_site != "all":
        sites_to_test = [target_site]
        
    bot = WebAutomation(headless=False)
    try:
        bot.start()
        for site in sites_to_test:
            test_site(site, bot, item, config)
            time.sleep(3)
    finally:
        bot.stop()
        print("\nHoàn tất kiểm tra!")

if __name__ == "__main__":
    main()
