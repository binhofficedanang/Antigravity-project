import json
import csv
import os
import time
import argparse
from web_automation import WebAutomation

# ============================================================
# DANH SÁCH KÊnh ĐANG HOẠT ĐỘNG (cập nhật 03/06/2026)
# ============================================================
# ✅ HOẠT ĐỘNG TỐT:
#   raovat.net, thuviennhadat.vn, 123nhadatviet.com,
#   nhadatviet247.net, muaban.net, phongtro123.com,
#   thuephongtro.com, muabandanang.vn, bds123.vn
# ❌ ĐÃ LOẠI:
#   rongbay.com      → VietID OAuth timeout
#   raovat247.net    → Domain dead (DNS không phân giải)
#   nhadat24h.net    → Cloudflare 403 permanent block
#   timkiemnhadat.vn → Đã đổi tên → infonhadat.com
#   chothuenha.com.vn → Yêu cầu nạp tiền để đăng tin
#   nhachothue.vn    → Yêu cầu đăng ký gói trả phí (xác nhận 03/06/2026)
#   datviet24h.com.vn → Login/session không ổn định (xác nhận 03/06/2026)
# ============================================================


def load_config(filepath="config.json"):
    if not os.path.exists(filepath):
        print(f"Không tìm thấy file {filepath}")
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def load_data(filepath="data.csv"):
    data = []
    if not os.path.exists(filepath):
        print(f"Không tìm thấy file {filepath}")
        return data
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def load_posted_history(filepath="posted_history.json"):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Không thể đọc file lịch sử: {e}")
        return []

def save_posted_history(history, filepath="posted_history.json"):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ Không thể lưu file lịch sử: {e}")

def normalize_string(s):
    import unicodedata
    import re
    s = s.lower().strip()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join([c for c in s if not unicodedata.combining(c)])
    s = s.replace('đ', 'd')
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

def is_already_posted(title, area, source_url, posted_history):
    import re
    match = re.search(r'/property/([^/]+)', source_url)
    slug = match.group(1) if match else ""
    slug_clean = slug.replace("toa-nha-", "")
    if not slug_clean:
        return False

    for hist_item in posted_history:
        if isinstance(hist_item, dict):
            if hist_item.get("status") == "Thất bại":
                continue
            hist_url = hist_item.get("source_url", "")
            hist_match = re.search(r'/property/([^/]+)', hist_url)
            hist_slug = hist_match.group(1) if hist_match else ""
            hist_slug_clean = hist_slug.replace("toa-nha-", "")
            if hist_slug_clean == slug_clean:
                return True
        else:
            hist_str = str(hist_item).lower()
            slug_spaced = slug_clean.replace("-", " ")
            if (slug_spaced in hist_str or
                    slug_clean in hist_str or
                    normalize_string(slug_clean) in normalize_string(hist_str)):
                return True
    return False

def run_ai_repair(site_name, headless=False):
    """Gọi ai_selector_generator.py bằng subprocess để tự động sửa/cập nhật selectors bằng AI."""
    import subprocess
    import sys
    
    python_path = sys.executable
    cmd = [python_path, "ai_selector_generator.py", "--site", site_name]
    if headless:
        cmd.append("--headless")
        
    print(f"⚙️ [AI-REPAIR] Đang chạy lệnh: {' '.join(cmd)}")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(res.stdout)
        return "AI đã phân tích và trích xuất thành công" in res.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi chạy AI Selector Generator: {e.stderr or e.stdout}")
        return False
def execute_channel_posting(site_name, account, target_item, bot, args, fallback_callback):
    """Thực thi luồng đăng tin cho một trang: Thử Hybrid -> Sửa AI (nếu có cờ) -> Chạy Fallback."""
    if not account:
        print(f"Bỏ qua {site_name} (chưa cấu hình tài khoản)")
        return False
        
    print(f"\n--- [{site_name.upper()}] ---")
    
    # 1. Thử chạy bằng Hybrid Selector Runner
    success = bot.post_by_selectors(site_name, account, target_item, dry_run=args.dry_run)
    if success:
        return True
        
    # 2. Nếu thất bại, thử chạy AI-Repair nếu được cấp cờ
    if args.ai_repair:
        print(f"🤖 [AI-REPAIR] Đăng tin bằng Hybrid Selector thất bại. Đang gọi AI Selector Generator...")
        repair_ok = run_ai_repair(site_name, args.headless)
        if repair_ok:
            # Thử chạy lại bằng Hybrid Selector sau khi đã cập nhật selectors
            print(f"🔄 [AI-REPAIR] Thử chạy lại Hybrid Selector sau khi cập nhật selectors...")
            success = bot.post_by_selectors(site_name, account, target_item, dry_run=args.dry_run)
            if success:
                return True
                
    # 3. Chạy bằng Fallback code cứng
    print(f"⚠️ Fallback về code cứng cho {site_name}...")
    try:
        return fallback_callback()
    except Exception as e:
        print(f"❌ Lỗi khi chạy fallback cho {site_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Poster Bot - Đăng tin bất động sản tự động")
    parser.add_argument("-s", "--site", type=str,
                        help="Chỉ chạy riêng cho một trang cụ thể (vd: raovat.net, thuviennhadat.vn)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Chế độ chạy thử, điền form nhưng không nhấn nút đăng tin")
    parser.add_argument("--ai-repair", action="store_true",
                        help="Tự động gọi AI sửa selectors nếu đăng tin bằng Hybrid Selector thất bại")
    parser.add_argument("--headless", action="store_true",
                        help="Chạy trình duyệt ở chế độ ẩn danh")
    args = parser.parse_args()

    print("--- POSTER BOT ---")
    config = load_config()
    data = load_data()

    if not data:
        print("Không có dữ liệu bài đăng. Vui lòng thêm vào data.csv.")
        return

    # Lọc bài viết chưa đăng
    posted_history = load_posted_history()
    pending_items = []
    for item in data:
        if not is_already_posted(
            item.get("title", ""), item.get("area", ""),
            item.get("source_url", ""), posted_history
        ):
            pending_items.append(item)

    if not pending_items:
        print("🎉 Tất cả các tin đăng trong data.csv đã được đăng hoàn tất trước đó!")
        return

    # Chọn 1 bài viết chưa đăng đầu tiên để xử lý
    target_item = pending_items[0]
    print(f"\n👉 Chọn bài viết mới để đăng: {target_item.get('title')}")

    # Cấu hình tài khoản
    bds123_account       = config.get("bds123.vn", {})
    raovat_account       = config.get("raovat.net", {})
    thuviennhadat_account = config.get("thuviennhadat.vn", {})
    muaban_account       = config.get("muaban.net", {})
    muabandanang_account = config.get("muabandanang.vn", {})
    phongtro123_account  = config.get("phongtro123.com", {})
    thuephongtro_account = config.get("thuephongtro.com", {})
    nhachothue_account   = config.get("nhachothue.vn", {})
    datviet24h_account   = config.get("datviet24h.com.vn", {})
    nhadatviet247_account = config.get("nhadatviet247.net", {})
    nhadatviet123_account = config.get("123nhadatviet.com", {})
    giaodichnhadat_account = config.get("giaodichnhadat.vn", {})
    thongtinnhadat_account = config.get("thongtinnhadat.vn", {})
    dangtinbatdongsan_account = config.get("dangtinbatdongsan.vn", {})
    luachonnhadat_account = config.get("luachonnhadat.vn", {})

    active_site = args.site.lower() if args.site else None
    if active_site:
        print(f"🎯 Chế độ lọc trang: Chỉ đăng lên kênh [{active_site}]")

    # Track kênh thành công/thất bại
    success_channels = []
    failed_channels  = []

    bot = WebAutomation(headless=args.headless)

    try:
        bot.start()

        # ============================================================
        # KÊNH 1: RAOVAT.NET ✅
        # ============================================================
        if not active_site or "raovat.net" in active_site:
            def fallback_raovat():
                bot.login_raovat_net(raovat_account["email"], raovat_account["password"])
                bot.post_raovat_net(target_item)
                return True
                
            if execute_channel_posting("raovat.net", raovat_account, target_item, bot, args, fallback_raovat):
                success_channels.append("raovat.net")
                time.sleep(5)
            else:
                failed_channels.append("raovat.net")

        # ============================================================
        # KÊNH 2: THUVIENNHADAT.VN ✅
        # ============================================================
        if not active_site or "thuviennhadat.vn" in active_site:
            def fallback_thuviennhadat():
                bot.login_thuviennhadat(thuviennhadat_account["username"], thuviennhadat_account["password"])
                bot.post_thuviennhadat(target_item)
                return True
                
            if execute_channel_posting("thuviennhadat.vn", thuviennhadat_account, target_item, bot, args, fallback_thuviennhadat):
                success_channels.append("thuviennhadat.vn")
                time.sleep(5)
            else:
                failed_channels.append("thuviennhadat.vn")

        # ============================================================
        # KÊNH 3: 123NHADATVIET.COM ✅
        # ============================================================
        if not active_site or "123nhadatviet.com" in active_site:
            def fallback_123nhadatviet():
                ok = bot.login_123nhadatviet(nhadatviet123_account["username"], nhadatviet123_account["password"])
                if ok:
                    bot.post_123nhadatviet(target_item)
                    return True
                return False
                
            if execute_channel_posting("123nhadatviet.com", nhadatviet123_account, target_item, bot, args, fallback_123nhadatviet):
                success_channels.append("123nhadatviet.com")
                time.sleep(5)
            else:
                failed_channels.append("123nhadatviet.com")

        # ============================================================
        # KÊNH 4: NHADATVIET247.NET ✅
        # ============================================================
        if not active_site or "nhadatviet247.net" in active_site:
            def fallback_nhadatviet247():
                ok = bot.login_nhadatviet247(nhadatviet247_account["username"], nhadatviet247_account["password"])
                if ok:
                    bot.post_nhadatviet247(target_item)
                    return True
                return False
                
            if execute_channel_posting("nhadatviet247.net", nhadatviet247_account, target_item, bot, args, fallback_nhadatviet247):
                success_channels.append("nhadatviet247.net")
                time.sleep(5)
            else:
                failed_channels.append("nhadatviet247.net")

        # ============================================================
        # KÊNH 5: MUABAN.NET ✅
        # ============================================================
        if not active_site or "muaban.net" in active_site:
            def fallback_muaban():
                ok = bot.login_muaban(muaban_account["username"], muaban_account["password"])
                if ok:
                    bot.post_muaban(target_item)
                    return True
                return False
                
            if execute_channel_posting("muaban.net", muaban_account, target_item, bot, args, fallback_muaban):
                success_channels.append("muaban.net")
                time.sleep(5)
            else:
                failed_channels.append("muaban.net")

        # ============================================================
        # KÊNH 6: PHONGTRO123.COM ✅
        # ============================================================
        if not active_site or "phongtro123.com" in active_site:
            def fallback_phongtro123():
                ok = bot.login_phongtro123(phongtro123_account["username"], phongtro123_account["password"])
                if ok:
                    bot.post_phongtro123(target_item)
                    return True
                return False
                
            if execute_channel_posting("phongtro123.com", phongtro123_account, target_item, bot, args, fallback_phongtro123):
                success_channels.append("phongtro123.com")
                time.sleep(5)
            else:
                failed_channels.append("phongtro123.com")

        # ============================================================
        # KÊNH 7: THUEPHONGTRO.COM ✅
        # ============================================================
        if not active_site or "thuephongtro.com" in active_site:
            def fallback_thuephongtro():
                ok = bot.login_thuephongtro(thuephongtro_account["username"], thuephongtro_account["password"])
                if ok:
                    bot.post_thuephongtro(target_item)
                    return True
                return False
                
            if execute_channel_posting("thuephongtro.com", thuephongtro_account, target_item, bot, args, fallback_thuephongtro):
                success_channels.append("thuephongtro.com")
                time.sleep(5)
            else:
                failed_channels.append("thuephongtro.com")

        # ============================================================
        # KÊNH 8: MUABANDANANG.VN 🔄
        # ============================================================
        if not active_site or "muabandanang.vn" in active_site:
            def fallback_muabandanang():
                ok = bot.login_muabandanang(muabandanang_account["username"], muabandanang_account["password"])
                if ok:
                    return bot.post_muabandanang(target_item)
                return False
                
            if execute_channel_posting("muabandanang.vn", muabandanang_account, target_item, bot, args, fallback_muabandanang):
                success_channels.append("muabandanang.vn")
                time.sleep(5)
            else:
                failed_channels.append("muabandanang.vn")

        # ============================================================
        # KÊnh 9: NHACHOTHUE.VN - ❌ ĐÃ VÔ HIỆU HÓA
        # Lý do: Yêu cầu đăng ký gói trả phí mới được đăng tin (đã xác nhận 03/06/2026)
        # ============================================================
        # if not active_site or "nhachothue.vn" in active_site:
        #     def fallback_nhachothue():
        #         ok = bot.login_nhachothue(
        #             nhachothue_account.get("email") or nhachothue_account.get("username"),
        #             nhachothue_account["password"]
        #         )
        #         if ok:
        #             return bot.post_nhachothue(target_item)
        #         return False
        #         
        #     if execute_channel_posting("nhachothue.vn", nhachothue_account, target_item, bot, args, fallback_nhachothue):
        #         success_channels.append("nhachothue.vn")
        #         time.sleep(5)
        #     else:
        #         failed_channels.append("nhachothue.vn")

        # ============================================================
        # KÊNH 10: DATVIET24H.COM.VN 🔄 - ❌ ĐÃ VÔ HIỆU HÓA
        # Lý do: Login/session không ổn định (xác nhận 03/06/2026)
        # ============================================================
        # if not active_site or "datviet24h.com.vn" in active_site:
        #     def fallback_datviet24h():
        #         ok = bot.login_datviet24h(datviet24h_account["username"], datviet24h_account["password"])
        #         if ok:
        #             return bot.post_datviet24h(target_item)
        #         return False
        #         
        #     if execute_channel_posting("datviet24h.com.vn", datviet24h_account, target_item, bot, args, fallback_datviet24h):
        #         success_channels.append("datviet24h.com.vn")
        #         time.sleep(5)
        #     else:
        #         failed_channels.append("datviet24h.com.vn")


        # ============================================================
        # KÊNH 11: BDS123.VN ✅
        # ============================================================
        if not active_site or "bds123.vn" in active_site:
            def fallback_bds123():
                ok = bot.login_bds123(
                    bds123_account.get("phone") or bds123_account.get("username"),
                    bds123_account["password"]
                )
                if ok:
                    return bot.post_bds123(target_item)
                return False
                
            if execute_channel_posting("bds123.vn", bds123_account, target_item, bot, args, fallback_bds123):
                success_channels.append("bds123.vn")
                time.sleep(5)
            else:
                failed_channels.append("bds123.vn")

        # ============================================================
        # KÊNH 12: GIAODICHNHADAT.VN ✅
        # ============================================================
        if not active_site or "giaodichnhadat.vn" in active_site:
            def fallback_giaodichnhadat():
                email_val = giaodichnhadat_account.get("email") or giaodichnhadat_account.get("username")
                pass_val  = giaodichnhadat_account.get("password")
                if email_val:
                    ok = bot.login_giaodichnhadat(email_val, pass_val)
                    if ok:
                        return bot.post_giaodichnhadat(target_item)
                return False
                
            if execute_channel_posting("giaodichnhadat.vn", giaodichnhadat_account, target_item, bot, args, fallback_giaodichnhadat):
                success_channels.append("giaodichnhadat.vn")
                time.sleep(5)
            else:
                failed_channels.append("giaodichnhadat.vn")

        # ============================================================
        # KÊNH 13: THONGTINNHADAT.VN ✅
        # ============================================================
        if not active_site or "thongtinnhadat.vn" in active_site:
            def fallback_thongtinnhadat():
                email_val = thongtinnhadat_account.get("email") or thongtinnhadat_account.get("username")
                pass_val  = thongtinnhadat_account.get("password")
                if email_val:
                    ok = bot.login_thongtinnhadat(email_val, pass_val)
                    if ok:
                        return bot.post_thongtinnhadat(target_item)
                return False
                
            if execute_channel_posting("thongtinnhadat.vn", thongtinnhadat_account, target_item, bot, args, fallback_thongtinnhadat):
                success_channels.append("thongtinnhadat.vn")
                time.sleep(5)
            else:
                failed_channels.append("thongtinnhadat.vn")

        # ============================================================
        # KÊNH 14: DANGTINBATDONGSAN.VN ✅
        # ============================================================
        if not active_site or "dangtinbatdongsan.vn" in active_site:
            def fallback_dangtinbatdongsan():
                user_val = dangtinbatdongsan_account.get("username") or dangtinbatdongsan_account.get("phone")
                pass_val = dangtinbatdongsan_account.get("password")
                if user_val:
                    ok = bot.login_dangtinbatdongsan(user_val, pass_val)
                    if ok:
                        return bot.post_dangtinbatdongsan(target_item)
                return False
                
            if execute_channel_posting("dangtinbatdongsan.vn", dangtinbatdongsan_account, target_item, bot, args, fallback_dangtinbatdongsan):
                success_channels.append("dangtinbatdongsan.vn")
                time.sleep(5)
            else:
                failed_channels.append("dangtinbatdongsan.vn")

        # ============================================================
        # KÊNH 15: LUACHONNHADAT.VN ✅
        # ============================================================
        if not active_site or "luachonnhadat.vn" in active_site:
            def fallback_luachonnhadat():
                email_val = luachonnhadat_account.get("username") or luachonnhadat_account.get("email")
                if email_val:
                    return bot.post_luachonnhadat(target_item)
                return False
                
            if execute_channel_posting("luachonnhadat.vn", luachonnhadat_account, target_item, bot, args, fallback_luachonnhadat):
                success_channels.append("luachonnhadat.vn")
                time.sleep(5)
            else:
                failed_channels.append("luachonnhadat.vn")

        # ============================================================
        # Tổng kết và lưu lịch sử
        # ============================================================
        print(f"\n🏁 Đã hoàn thành tiến trình đăng bài trên tất cả các trang được chọn!")
        if success_channels:
            print(f"✅ Đăng tin thành công trên các kênh: {', '.join(success_channels)}")
        if failed_channels:
            print(f"❌ Đăng tin thất bại trên các kênh: {', '.join(failed_channels)}")

        if not active_site:
            posted_history.append({
                "title":      target_item.get("title"),
                "area":       target_item.get("area"),
                "source_url": target_item.get("source_url"),
                "posted_at":  time.strftime("%Y-%m-%d %H:%M:%S"),
                "status":     "Thành công" if success_channels else "Thất bại",
                "channels":   ", ".join(success_channels) if success_channels else "Không có",
                "log_file":   f"run_{time.strftime('%Y%m%d_%H%M%S')}.log"
            })
            save_posted_history(posted_history)
            print(f"\n💾 Đã lưu '{target_item.get('title')}' vào lịch sử đăng bài.")
        else:
            print("\n⚠️ Chạy ở chế độ lọc trang (--site), không lưu lịch sử.")

    except KeyboardInterrupt:
        print("\nĐã dừng bot thủ công.")
    finally:
        bot.stop()
        print("--- KẾT THÚC ---")

if __name__ == "__main__":
    main()
