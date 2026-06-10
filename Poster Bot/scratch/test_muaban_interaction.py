#!/usr/bin/env python3
"""
Interactive test to fill the form on muaban.net and take screenshots at each step,
including clicking 'Tiếp tục' to see if it moves to the next step or shows validation errors.
"""
import sys, os, time, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

def ss(bot, name):
    scr_dir = os.path.dirname(os.path.abspath(__file__))
    bot.safe_screenshot(os.path.join(scr_dir, name))
    print(f"📸 Captured screenshot: {name}")

def main():
    # Read the item from data.csv
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data.csv")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        item = next(reader)
        # Let's use the one with larger area/price if possible, or just the first one
        # Let's print the item title
        print(f"Using test item: {item.get('title')}")

    bot = WebAutomation(headless=False)
    try:
        bot.start()
        
        # 1. Login
        import json
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        muaban_config = config.get("muaban.net", {})
        username = muaban_config.get("username", "")
        password = muaban_config.get("password", "")
        
        print("Logging in...")
        login_ok = bot.login_muaban(username, password)
        if not login_ok:
            print("❌ Login failed")
            return
            
        # 2. Go to posting page
        print("Navigating to posting page...")
        bot.page.goto("https://muaban.net/dang-tin", wait_until="domcontentloaded", timeout=60000)
        bot._wait_for_cloudflare(bot.page, timeout_secs=15)
        time.sleep(3)
        ss(bot, "inter01_loaded.png")
        
        # 3. Dismiss draft modal
        try:
            new_btn = bot.page.locator("button:has-text('Đăng tin mới')").first
            if new_btn.count() > 0 and new_btn.is_visible():
                new_btn.click(timeout=4000)
                print("Clicked 'Đăng tin mới'")
                time.sleep(2)
                ss(bot, "inter02_modal_dismissed.png")
        except Exception as e:
            print(f"No draft modal or error: {e}")
            
        # 4. Select category
        print("Selecting category...")
        bot.page.locator("text=Bất động sản").first.click(timeout=5000)
        time.sleep(1)
        bot.page.locator("text=Cho thuê").first.click(timeout=5000)
        time.sleep(1)
        bot.page.locator("text=Văn phòng, mặt bằng").first.click(timeout=5000)
        time.sleep(2)
        ss(bot, "inter03_category_selected.png")
        
        # 5. Fill fields
        print("Filling fields...")
        title = item.get('title', '')
        content = item.get('content', '').replace('\\n', '\n')
        price_val = bot.parse_price(item.get('price', ''), item.get('area', ''))
        area_val = str(item.get('area', ''))
        address_val = item.get('address', '')
        district_val = item.get('district', '')
        
        # Title
        bot.page.locator("input[name='title']").first.fill(title, timeout=4000)
        # Body
        bot.page.locator("textarea[name='body']").first.fill(content, timeout=4000)
        # Price
        if price_val > 0:
            bot.page.locator("input[name='price']").first.fill(str(price_val), timeout=4000)
        # Area
        if area_val:
            bot.page.locator("input[name='living_area']").first.fill(area_val, timeout=4000)
            
        ss(bot, "inter04_fields_filled.png")
        
        # 6. Location
        print("Selecting location...")
        
        # Parse the address to extract ward and street details
        ward_val = ""
        street_val = ""
        street_number_val = ""
        
        addr_parts = [p.strip() for p in address_val.split(',') if p.strip()]
        if len(addr_parts) >= 4:
            street_val = addr_parts[0]
            ward_val = addr_parts[1]
        elif len(addr_parts) == 3:
            first_part = addr_parts[0]
            if "Phường" in first_part or "Xã" in first_part:
                ward_val = first_part
            else:
                street_val = first_part
        else:
            street_val = address_val
            
        # Fallback ward_val if empty
        if not ward_val and district_val:
            import re
            district_clean = district_val.replace("Quận", "").replace("Huyện", "").strip()
            default_wards = {
                "Hải Châu": "Bình Thuận",
                "Thanh Khê": "Thạc Gián",
                "Liên Chiểu": "Hòa Minh",
                "Sơn Trà": "An Hải Bắc",
                "Ngũ Hành Sơn": "Mỹ An",
                "Cẩm Lệ": "Khuê Trung",
                "Hòa Vang": "Hòa Châu"
            }
            ward_val = default_wards.get(district_clean, "Bình Thuận")
            print(f"Using default ward: {ward_val}")

        # Parse house number if present at the start of street_val
        if street_val:
            import re
            num_match = re.match(r'^(\d+[a-zA-Z]?(\/\d+[a-zA-Z]?)?)\s+(.*)$', street_val)
            if num_match:
                street_number_val = num_match.group(1)
                street_val = num_match.group(3).strip()

        print(f"Parsed address values -> Street: {street_val} | Number: {street_number_val} | Ward: {ward_val} | District: {district_val}")

        def select_modal(trigger_id, value_text, label_name):
            if not value_text:
                return
            try:
                trigger = bot.page.locator(f"div#{trigger_id}")
                # Wait for field to be enabled (some fields are disabled until parent is selected)
                for _ in range(5):
                    cls = trigger.get_attribute("class") or ""
                    if "disable" not in cls:
                        break
                    time.sleep(1)
                
                try:
                    trigger.click(timeout=3000)
                except Exception as click_err:
                    print(f"  - Trigger click standard failed: {click_err}. Trying JS click...")
                    trigger.evaluate("el => el.click()")
                time.sleep(1.5)
                
                # Check if there's a search input
                search_input = bot.page.locator("div[class*='modal'] input[type='text'], input[placeholder*='Nhập để tìm']").first
                if search_input.count() > 0 and search_input.is_visible():
                    search_input.fill(value_text, timeout=3000)
                    time.sleep(1.5)
                
                # Use evaluate to find the option element in the DOM
                option_handle = bot.page.evaluate_handle(
                    """(val) => {
                        const modal = document.querySelector('[class*="modal"]');
                        if (!modal) return null;
                        
                        const elements = Array.from(modal.querySelectorAll('div, li, span, p'));
                        const searchVal = val.toLowerCase().trim();
                        
                        // Filter elements containing the text
                        const matches = elements.filter(el => {
                            if (!el.innerText) return false;
                            const text = el.innerText.toLowerCase();
                            // Must contain the value
                            if (!text.includes(searchVal)) return false;
                            // Exclude modal header, close button, search input
                            if (el.tagName === 'INPUT' || el.tagName === 'BUTTON' || el.tagName === 'SVG') return false;
                            const cls = (el.className || "").toString();
                            if (cls.includes('header') || cls.includes('search') || cls.includes('close')) return false;
                            return true;
                        });
                        
                        if (matches.length > 0) {
                            // Find the leaf elements (inner-most match)
                            const leaves = matches.filter(el => {
                                return !matches.some(other => other !== el && el.contains(other));
                            });
                            if (leaves.length > 0) return leaves[0];
                        }
                        
                        // Fallback: Find the first option-like leaf element in the list container
                        const allOptionLeaves = elements.filter(el => {
                            if (el.tagName === 'INPUT' || el.tagName === 'BUTTON' || el.tagName === 'SVG') return false;
                            const cls = (el.className || "").toString();
                            if (cls.includes('header') || cls.includes('search') || cls.includes('close') || cls.includes('title')) return false;
                            if (!el.innerText || !el.innerText.trim()) return false;
                            return true;
                        }).filter((el, idx, selfList) => {
                            return !selfList.some(other => other !== el && el.contains(other));
                        });
                        
                        return allOptionLeaves[0] || null;
                    }""", value_text
                )
                
                if option_handle and option_handle.as_element():
                    option = option_handle.as_element()
                    try:
                        option.click(timeout=3000)
                    except:
                        option.evaluate("el => el.click()")
                    time.sleep(1.5)
                    print(f"Selected {label_name}: {value_text}")
                else:
                    raise Exception(f"No option or fallback item found for {label_name}")
            except Exception as e:
                print(f"Error {label_name}: {e}")
                # Close modal if open
                try:
                    close_btn = bot.page.locator("div[class*='modal'] button, div[class*='modal'] svg, div[class*='modal'] [class*='close']").first
                    if close_btn.count() > 0 and close_btn.is_visible():
                        close_btn.click(timeout=2000)
                    else:
                        bot.page.keyboard.press("Escape")
                    time.sleep(0.5)
                except: pass

        select_modal("city_id", "Đà Nẵng", "City")
        select_modal("district_id", district_val if district_val else "Sơn Trà", "District")
        select_modal("ward_id", ward_val, "Ward")
        select_modal("street_id", street_val, "Street")
        
        # Street number (Số nhà) input
        if street_number_val:
            try:
                bot.page.locator("input[name='street_number']").first.fill(street_number_val, timeout=3000)
                print(f"Filled street number: {street_number_val}")
            except Exception as e:
                print(f"Error filling street number: {e}")
            
        # Property subtype
        select_modal("property_subtype", "Văn phòng", "Property Subtype")
        
        ss(bot, "inter05_location_filled.png")
        
        # 7. Images
        # Let's skip downloading and use dummy image files if they don't exist
        dummy_images = []
        for i in range(1, 4):
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"test_img_{i}.png")
            if not os.path.exists(img_path):
                # Create a small dummy png file
                with open(img_path, 'wb') as dummy_f:
                    dummy_f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82')
            dummy_images.append(img_path)
            
        print("Uploading images...")
        file_input = bot.page.locator("input[type='file']")
        if file_input.count() > 0:
            file_input.first.set_input_files(dummy_images)
            time.sleep(4)
            
        ss(bot, "inter06_images_uploaded.png")
        
        # 8. Click 'Tiếp tục'
        print("Clicking 'Tiếp tục'...")
        try:
            continue_btn = bot.page.locator("button:has-text('Tiếp tục')").last
            try:
                continue_btn.click(timeout=4000)
            except Exception as click_err:
                print(f"  - Standard continue click failed: {click_err}. Trying JS click...")
                continue_btn.evaluate("btn => btn.click()")
        except Exception as resolve_err:
            print(f"  - Locator resolution failed: {resolve_err}. Trying direct document select click...")
            bot.page.evaluate("() => { const btns = Array.from(document.querySelectorAll('button')); const btn = btns.find(b => b.innerText.includes('Tiếp tục')); if (btn) btn.click(); }")
        time.sleep(5)
        ss(bot, "inter07_after_continue.png")
        
        # Check if there are errors on the page
        errors = bot.page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('[class*="error"], [class*="Error"], .text-danger, .invalid-feedback').forEach(el => {
                    if (el.innerText && el.innerText.trim()) {
                        results.push(el.innerText.trim());
                    }
                });
                return results;
            }
        """)
        if errors:
            print("\n❌ Page validation errors found:")
            for err in errors:
                print(f"  - {err}")
        else:
            print("\nNo validation errors found on screen.")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
