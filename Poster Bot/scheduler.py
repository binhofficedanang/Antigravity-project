import os
import json
import time
import threading
from datetime import datetime
from web_automation import WebAutomation

# Đường dẫn file hàng đợi
BOT_DIR = os.path.dirname(os.path.abspath(__file__))
QUEUE_FILE = os.path.join(BOT_DIR, "scheduler_queue.json")
CONFIG_FILE = os.path.join(BOT_DIR, "config.json")
HISTORY_FILE = os.path.join(BOT_DIR, "posted_history.json")

def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    try:
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_queue(queue):
    try:
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(queue, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False

def run_scheduled_task(task):
    """Thực thi một tác vụ đăng tin hẹn giờ"""
    print(f"\n⏰ [SCHEDULER] Bắt đầu chạy tác vụ hẹn giờ: {task.get('id')} - {task['item'].get('title')}")
    item = task["item"]
    channels = task["channels"]
    
    # Load cấu hình accounts
    accounts = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                accounts = json.load(f)
        except Exception:
            pass

    success_channels = []
    failed_channels = []
    
    bot = None
    try:
        # Hẹn giờ thì mặc định chạy ẩn danh (headless=True)
        bot = WebAutomation(headless=True)
        bot.start()
        
        # Đăng lên từng kênh được chỉ định
        for site_key in channels:
            # Lấy tài khoản được chỉ định hoặc mặc định từ config
            acc = task.get("accounts", {}).get(site_key, {})
            if not acc:
                # Fallback lấy tài khoản đầu tiên hoặc cấu hình cũ
                accs = accounts.get("accounts", {}).get(site_key, [])
                if accs:
                    acc = accs[0]
                else:
                    acc = accounts.get(site_key, {})

            if site_key == "rongbay.com" and acc.get("username"):
                login_ok = bot.login_rongbay(acc.get("username"), acc.get("password"))
                if login_ok and bot.post_rongbay(item):
                    success_channels.append(site_key)
                else:
                    failed_channels.append(site_key)
            elif site_key == "raovat.net" and acc.get("email"):
                login_ok = bot.login_raovat_net(acc.get("email"), acc.get("password"))
                if login_ok and bot.post_raovat_net(item):
                    success_channels.append(site_key)
                else:
                    failed_channels.append(site_key)
            elif site_key == "thuviennhadat.vn" and acc.get("username"):
                login_ok = bot.login_thuviennhadat(acc.get("username"), acc.get("password"))
                if login_ok and bot.post_thuviennhadat(item):
                    success_channels.append(site_key)
                else:
                    failed_channels.append(site_key)
            elif site_key == "muaban.net" and acc.get("username"):
                login_ok = bot.login_muaban(acc.get("username"), acc.get("password"))
                if login_ok and bot.post_muaban(item):
                    success_channels.append(site_key)
                else:
                    failed_channels.append(site_key)
            else:
                failed_channels.append(site_key)

    except Exception as e:
        print(f"❌ [SCHEDULER] Lỗi chạy tác vụ: {e}")
    finally:
        if bot:
            try:
                bot.stop()
            except Exception:
                pass

    # Cập nhật kết quả vào lịch sử chung
    if success_channels:
        try:
            posted_history = []
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    posted_history = json.load(f)
            posted_history.append({
                "title": item.get("title"),
                "area": item.get("area"),
                "price": item.get("price"),
                "address": item.get("address"),
                "district": item.get("district"),
                "source_url": item.get("source_url"),
                "posted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Thành công" if success_channels else "Thất bại",
                "channels": success_channels
            })
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(posted_history, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    return success_channels, failed_channels

def scheduler_loop():
    """Vòng lặp chạy nền kiểm tra hàng đợi hẹn giờ"""
    print("⏰ [SCHEDULER] Trình chạy nền lịch trình hẹn giờ đã được khởi động.")
    while True:
        try:
            queue = load_queue()
            now = datetime.now()
            updated = False
            
            for task in queue:
                if task.get("status") == "Chờ chạy":
                    sched_time = datetime.strptime(task["scheduled_time"], "%Y-%m-%d %H:%M:%S")
                    if now >= sched_time:
                        task["status"] = "Đang chạy"
                        save_queue(queue)
                        
                        success, failed = run_scheduled_task(task)
                        
                        task["status"] = "Thành công" if success else "Thất bại"
                        task["result_channels"] = success
                        task["failed_channels"] = failed
                        task["executed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        updated = True
                        break
            
            if updated:
                save_queue(queue)
        except Exception as loop_err:
            print(f"❌ [SCHEDULER] Lỗi vòng lặp: {loop_err}")
            
        time.sleep(30)

_scheduler_started = False
def start_scheduler():
    """Khởi động Thread chạy nền nếu chưa được chạy"""
    global _scheduler_started
    if not _scheduler_started:
        t = threading.Thread(target=scheduler_loop, daemon=True)
        t.start()
        _scheduler_started = True
