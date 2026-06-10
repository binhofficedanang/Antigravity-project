#!/usr/bin/env python3
"""
Test muaban.net post form filling.
Goes through category → address → fields, takes screenshots, does NOT submit.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

SCREENSHOT_DIR = os.path.dirname(os.path.abspath(__file__))

def ss(bot, name):
    bot.safe_screenshot(os.path.join(SCREENSHOT_DIR, name))

def main():
    bot = WebAutomation(headless=False)
    try:
        bot.start()

        # 1. Login
        ok = bot.login_muaban("0935723727", "Binh1995@")
        if not ok:
            print("❌ Login failed"); return

        # 2. Go to post page
        bot.page.goto("https://muaban.net/dang-tin", wait_until="domcontentloaded", timeout=60000)
        bot._wait_for_cloudflare(bot.page, timeout_secs=15)
        time.sleep(3)
        ss(bot, "post01_dang_tin.png")

        # 3. Handle draft modal
        try:
            new_btn = bot.page.locator("button:has-text('Đăng tin mới')")
            if new_btn.count() > 0 and new_btn.first.is_visible():
                new_btn.first.click(timeout=3000)
                time.sleep(2)
                print("- Đã bấm 'Đăng tin mới'")
        except: pass

        # 4. Select category: Bất động sản > Cho thuê > Văn phòng, mặt bằng
        print("- Chọn danh mục...")
        for cat in ["Bất động sản", "Cho thuê", "Văn phòng, mặt bằng"]:
            try:
                bot.page.locator(f"text={cat}").first.click(timeout=5000)
                time.sleep(1.5)
                print(f"  ✓ {cat}")
            except Exception as e:
                print(f"  ⚠️ Không click được '{cat}': {e}")

        time.sleep(2)
        ss(bot, "post02_category.png")

        # 5. Fill basic info
        print("- Điền thông tin cơ bản...")
        try:
            bot.page.locator("input[name='title']").first.fill("Cho thuê văn phòng đẹp Đà Nẵng", timeout=4000)
            print("  ✓ Tiêu đề")
        except Exception as e: print(f"  ⚠️ Tiêu đề: {e}")

        try:
            bot.page.locator("textarea[name='body']").first.fill(
                "Văn phòng cho thuê tại Đà Nẵng. Diện tích linh hoạt, giá tốt.", timeout=4000)
            print("  ✓ Mô tả")
        except Exception as e: print(f"  ⚠️ Mô tả: {e}")

        try:
            bot.page.locator("input[name='living_area']").first.fill("50", timeout=4000)
            print("  ✓ Diện tích (living_area)")
        except Exception as e: print(f"  ⚠️ Diện tích: {e}")

        try:
            bot.page.locator("input[name='price']").first.fill("5000000", timeout=4000)
            print("  ✓ Giá")
        except Exception as e: print(f"  ⚠️ Giá: {e}")

        time.sleep(1)
        ss(bot, "post03_basic_info.png")

        # 6. Select location via modals
        print("- Chọn địa chỉ...")

        def select_modal(trigger_id, value, label):
            try:
                trigger = bot.page.locator(f"div#{trigger_id}")
                if trigger.count() == 0:
                    print(f"  ⚠️ Không tìm thấy #{trigger_id}")
                    return False
                trigger.click(timeout=5000)
                time.sleep(2)
                ss(bot, f"post_modal_{trigger_id}.png")

                option = bot.page.locator(f"text={value}").first
                if option.count() == 0:
                    option = bot.page.locator(f"li:has-text('{value}')").first
                option.click(timeout=5000)
                time.sleep(2)
                print(f"  ✓ {label}: {value}")
                return True
            except Exception as e:
                print(f"  ⚠️ {label}: {e}")
                try: bot.page.keyboard.press("Escape")
                except: pass
                time.sleep(0.5)
                return False

        select_modal("city_id", "Đà Nẵng", "Thành phố")
        select_modal("district_id", "Hải Châu", "Quận")
        select_modal("ward_id", "Hải Châu 1", "Phường")  # Try common ward

        # Street number
        try:
            bot.page.locator("input[name='street_number']").first.fill("123 Lê Duẩn", timeout=3000)
            print("  ✓ Số nhà")
        except Exception as e: print(f"  ⚠️ Số nhà: {e}")

        time.sleep(2)
        ss(bot, "post04_address_filled.png")
        print("✅ Test hoàn tất - KHÔNG submit form")

    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
