import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_automation import WebAutomation

def main():
    bot = WebAutomation(headless=True)
    bot.start()
    
    mock_item = {
        "title": "Bán căn hộ chung cư 2 phòng ngủ giá rẻ cực đẹp tại Đà Nẵng",
        "content": "Căn hộ thiết kế hiện đại, đầy đủ tiện nghi, vị trí đắc địa giao thông thuận tiện. Phù hợp cho hộ gia đình định cư lâu dài hoặc đầu tư cho thuê.",
        "category": "Văn phòng",
        "address": "123 Đường Nguyễn Văn Linh, Hải Châu, Đà Nẵng",
        "district": "Hải Châu",
        "area": "75",
        "price": "2.5 tỷ",
        "contact_name": "Nguyễn Văn A",
        "phone": "0905123456"
    }
    
    try:
        # Patch post_123nhadatviet_shared to not submit the form
        original_post_shared = bot.post_123nhadatviet_shared
        
        def patched_post_shared(base_url, item):
            print(f"[TEST] Running patched post on {base_url}...")
            # Navigate
            bot.page.goto(f"http://{base_url}/dang-tin.html", wait_until="domcontentloaded")
            bot._wait_for_cloudflare(bot.page, timeout_secs=15)
            time.sleep(2)
            
            # Fill Title
            title = item.get("title", "")
            bot.page.fill("#tieude", title)
            
            # Fill Content
            content = item.get("content") or item.get("description", "")
            bot.page.fill("#noidung", content)
            print(f"Filled content length: {len(content)}")
            
            # Category
            title_lower = title.lower()
            category_lower = (item.get("category") or "").lower()
            post_type = item.get("type", "Thuê").lower()
            
            loaitin_val = "2"
            if "bán" in title_lower or "ban" in title_lower or "bán" in category_lower or "ban" in category_lower or "bán" in post_type or "ban" in post_type:
                loaitin_val = "1"
            bot.page.select_option("#loaitin", loaitin_val)
            print(f"Selected category: {loaitin_val}")
            
            # Property type
            bds_type = (item.get("category") or item.get("property_type") or "").lower()
            loaibds_val = "2"
            if "chung cư" in bds_type or "căn hộ" in bds_type or "apartment" in bds_type or "chung cu" in bds_type or "can ho" in bds_type:
                loaibds_val = "4"
            elif "biệt thự" in bds_type or "biet thu" in bds_type:
                loaibds_val = "3"
            elif "văn phòng" in bds_type or "van phong" in bds_type:
                loaibds_val = "6"
            bot.page.select_option("#loaibds", loaibds_val)
            print(f"Selected property type: {loaibds_val}")
            
            # City mapping
            address_lower = item.get("address", "").lower()
            tinh_val = "1"
            if "đà nẵng" in address_lower or "da nang" in address_lower or "đà nẵng" in title_lower or "da nang" in title_lower:
                tinh_val = "3"
            bot.page.select_option("#tinh", tinh_val)
            print(f"Selected city: {tinh_val}")
            time.sleep(1.5)
            
            # District mapping
            district_name = item.get("district", "").lower()
            district_options = bot.page.evaluate("""() => {
                const sel = document.getElementById('huyen');
                if (!sel) return [];
                return Array.from(sel.options).map(o => ({ value: o.value, text: o.text.toLowerCase() }));
            }""")
            print(f"Districts found: {len(district_options)}")
            huyen_val = ""
            for opt in district_options:
                if district_name in opt["text"] or opt["text"] in district_name:
                    huyen_val = opt["value"]
                    break
            if huyen_val:
                bot.page.select_option("#huyen", huyen_val)
                print(f"Selected district value: {huyen_val}")
                
            bot.page.fill("#diachi", item["address"])
            bot.page.fill("#dientich", item["area"])
            bot.page.fill("#gia", "2500000")
            bot.page.select_option("#cachtinh", "1")
            
            bot.page.fill("#lienhe", item["contact_name"])
            bot.page.fill("#dienthoai", item["phone"])
            
            # Solve captcha
            captcha_code = bot.solve_image_captcha(bot.page, "img.captchagenerator")
            print(f"Solved Captcha Code: '{captcha_code}'")
            
            # Screenshot
            script_dir = os.path.dirname(os.path.abspath(__file__))
            bot.safe_screenshot(os.path.join(script_dir, f"test_{base_url.replace('.', '_')}_success.png"))
            print(f"Dry run complete for {base_url}")
            return True
            
        bot.post_123nhadatviet_shared = patched_post_shared
        
        # Test 123nhadatviet
        bot.post_123nhadatviet(mock_item)
        
    except Exception as e:
        print("Error:", e)
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
