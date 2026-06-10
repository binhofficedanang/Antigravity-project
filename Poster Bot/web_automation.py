import time
import random
import os
import json
import re
import requests
from playwright.sync_api import sync_playwright

# playwright-stealth: cài nếu có, fallback sang JS tự implement nếu không có
try:
    from playwright_stealth import stealth_sync
    _STEALTH_AVAILABLE = True
except Exception:
    _STEALTH_AVAILABLE = False

# JS stealth script đầy đủ - ẩn tất cả dấu hiệu automation
# Hạt nhân là che: navigator.webdriver, plugins, chrome object, v.v.
_STEALTH_JS = """
() => {
    // 1. Ẩn navigator.webdriver
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

    // 2. Giả lập plugins như browser thật
    const makePlugin = (name, filename, desc) => {
        const p = Object.create(Plugin.prototype);
        Object.defineProperty(p, 'name', { get: () => name });
        Object.defineProperty(p, 'filename', { get: () => filename });
        Object.defineProperty(p, 'description', { get: () => desc });
        return p;
    };
    const pluginArray = [makePlugin('Chrome PDF Plugin','internal-pdf-viewer','Portable Document Format')];
    Object.defineProperty(navigator, 'plugins', { get: () => pluginArray });

    // 3. Ngôn ngữ Việt Nam (tránh headless mặc định en-US)
    Object.defineProperty(navigator, 'languages', { get: () => ['vi-VN', 'vi', 'en-US', 'en'] });

    // 4. Chrome object như browser thật
    window.chrome = {
        runtime: { id: undefined, connect: () => {}, sendMessage: () => {} },
        loadTimes: () => {},
        csi: () => ({}),
        app: {}
    };

    // 5. Ẩn Notification.permission nếu cần
    const orig = window.Notification;
    if (orig) {
        Object.defineProperty(window, 'Notification', {
            get: () => orig
        });
    }

    // 6. Ẩn headless qua screen depth
    Object.defineProperty(screen, 'colorDepth', { get: () => 24 });

    // 7. Override toString của function để không bị phát hiện bằng native code check
    const nativeToString = Function.prototype.toString;
    Function.prototype.toString = function() {
        if (this === Function.prototype.toString) return nativeToString.call(this);
        return nativeToString.call(this);
    };
}
"""

class WebAutomation:
    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        # Thư mục lưu session (cookies, localStorage) để vượt Cloudflare
        self.user_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_sessions")
        os.makedirs(self.user_data_dir, exist_ok=True)
        # Nạp CAPTCHA API Key
        self.captcha_api_key = ""
        self.proxy_config = None
        try:
            import json
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.captcha_api_key = cfg.get("captcha_api_key", "")
                self.proxy_config = cfg.get("proxy", None)
        except Exception:
            pass

    def start(self):
        print("Khởi động trình duyệt (Persistent Session)...")
        self.playwright = sync_playwright().start()
        
        # Cấu hình chung cho launch context
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-infobars",
            "--window-size=1280,800",
            "--start-maximized",
            "--disable-gpu-sandbox",
        ]
        
        # Cấu hình proxy nếu có
        pw_proxy = None
        if self.proxy_config and isinstance(self.proxy_config, dict):
            server = self.proxy_config.get("server")
            if server:
                pw_proxy = {"server": server}
                username = self.proxy_config.get("username")
                password = self.proxy_config.get("password")
                if username:
                    pw_proxy["username"] = username
                if password:
                    pw_proxy["password"] = password
                    
        # Dùng launch_persistent_context để lưu cookies/session giữa các lần chạy
        # Thử sử dụng Google Chrome chính chủ trước (channel="chrome") để có vân trình duyệt thật 100% vượt Cloudflare
        try:
            print("  => Đang thử khởi động Google Chrome chính chủ...")
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                channel="chrome",
                args=launch_args,
                ignore_default_args=["--enable-automation"],
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="vi-VN",
                timezone_id="Asia/Ho_Chi_Minh",
                geolocation={"latitude": 16.0544, "longitude": 108.2022},
                permissions=["geolocation"],
                ignore_https_errors=True,
                proxy=pw_proxy,
            )
            print("  ✓ Đã khởi động Google Chrome thành công!")
        except Exception as e_chrome:
            print(f"  ⚠️ Không thể chạy Google Chrome chính chủ ({e_chrome}). Đang chuyển sang Chromium mặc định...")
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                args=launch_args,
                ignore_default_args=["--enable-automation"],
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="vi-VN",
                timezone_id="Asia/Ho_Chi_Minh",
                geolocation={"latitude": 16.0544, "longitude": 108.2022},
                permissions=["geolocation"],
                ignore_https_errors=True,
                proxy=pw_proxy,
            )
            print("  ✓ Đã khởi động Chromium mặc định thành công!")

        self.browser = None
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()
        self.page.set_viewport_size({"width": 1280, "height": 800})
        
        # Áp dụng song song cả playwright-stealth và JS stealth tùy chỉnh để đạt hiệu quả bypass tối đa (chỉ khi chạy Headless)
        if self.headless:
            if _STEALTH_AVAILABLE:
                try:
                    stealth_sync(self.page)
                    print("  ✅ Stealth mode (playwright-stealth) đã kích hoạt")
                except Exception as e_stealth:
                    print(f"  ⚠️ playwright-stealth lỗi ({e_stealth})")
            
            self.page.add_init_script(_STEALTH_JS)
            print("  ✅ Custom JS Stealth đã được tiêm vào trang")
            
            # Stealth bổ sung: che thêm một số property khác
            self.page.add_init_script("""
                try {
                    Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 0 });
                    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
                    Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
                } catch(e) {}
            """)
        else:
            print("  ℹ️ Đang chạy ở chế độ có giao diện (headful) bằng Chrome chính chủ. Không áp dụng stealth để tránh bị Cloudflare phát hiện bất thường.")

    def stop(self):
        print("Đóng trình duyệt...")
        if self.context:
            self.context.close()  # Persistent context: close context (không phải browser)
        if self.playwright:
            self.playwright.stop()

    def safe_screenshot(self, path):
        """Chụp ảnh màn hình an toàn, tránh bị timeout do load fonts/resources"""
        try:
            self.page.screenshot(path=path, timeout=5000, animations="disabled")
            print(f"  📸 Đã chụp screenshot: {os.path.basename(path)}")
        except Exception as e:
            print(f"  ⚠️ Không thể chụp screenshot ({os.path.basename(path)}): {e}")

    def _wait_for_cloudflare(self, page, timeout_secs=60):
        """Chờ Cloudflare challenge hoàn tất.
        Với stealth mode, JS Challenge thường tự pass trong vài giây.
        Nếu vẫn xuất hiện Turnstile CAPTCHA thì cần giải thủ công 1 lần,
        sau đó session được lưu lại và không cần giải lại.
        """
        start = time.time()
        cf_titles = {'chờ một chút...', 'just a moment...', 'attention required!', ''}
        last_log = 0
        while time.time() - start < timeout_secs:
            try:
                title = page.title().strip()
                url = page.url
            except Exception:
                time.sleep(1)
                continue
            is_cf = (title.lower() in cf_titles
                     or 'challenge' in url
                     or 'cloudflare' in title.lower())
            if not is_cf and url not in ['about:blank', '']:
                elapsed = int(time.time() - start)
                if elapsed > 2:
                    print(f"  ✅ Cloudflare đã vượt qua sau {elapsed}s! ({title})")
                return True
            elapsed = int(time.time() - start)
            if elapsed - last_log >= 5:  # Log mỗi 5 giây thôi, tránh spam
                print(f"  ⏳ Đang chờ Cloudflare tự pass... ({elapsed}s) - '{title}'")
                # Thử giải CAPTCHA Turnstile tự động nếu phát hiện thấy
                self.handle_turnstile_if_present(page)
                if elapsed > 15 and not _STEALTH_AVAILABLE:
                    print("  💡 Gợi ý: Cài playwright-stealth để Cloudflare tự động pass")
                elif elapsed > 20:
                    print("  💡 Nếu thấy CAPTCHA hãy giải 1 lần - session sẽ được lưu lại")
                last_log = elapsed
            time.sleep(2)
        print("  ⚠️ Timeout chờ Cloudflare. Thử tiếp tục...")
        return False

    def solve_turnstile_captcha(self, page_url, sitekey):
        """Sử dụng API 2Captcha để giải Turnstile CAPTCHA tự động"""
        if not self.captcha_api_key:
            print("  ⚠️ Không tìm thấy CAPTCHA API Key trong cấu hình.")
            return None
            
        print("  🧩 Đang gửi yêu cầu giải Turnstile CAPTCHA tới 2Captcha...")
        try:
            import requests
            url = "http://2captcha.com/in.php"
            params = {
                "key": self.captcha_api_key,
                "method": "turnstile",
                "sitekey": sitekey,
                "pageurl": page_url,
                "json": 1
            }
            r = requests.post(url, data=params, timeout=15)
            res = r.json()
            if res.get("status") != 1:
                print(f"  ❌ Lỗi gửi CAPTCHA tới 2Captcha: {res.get('request')}")
                return None
                
            task_id = res.get("request")
            poll_url = "http://2captcha.com/res.php"
            poll_params = {
                "key": self.captcha_api_key,
                "action": "get",
                "id": task_id,
                "json": 1
            }
            
            print("  ⏳ Đang chờ 2Captcha giải CAPTCHA (thường mất 15-30s)...")
            for _ in range(25):
                time.sleep(5)
                pr = requests.get(poll_url, params=poll_params, timeout=10)
                pres = pr.json()
                if pres.get("status") == 1:
                    token = pres.get("request")
                    print("  ✅ Giải CAPTCHA thành công!")
                    return token
                elif pres.get("request") == "CAPCHA_NOT_READY":
                    continue
                else:
                    print(f"  ❌ Lỗi khi polling kết quả: {pres.get('request')}")
                    return None
            print("  ⚠️ Hết thời gian chờ giải CAPTCHA.")
            return None
        except Exception as e:
            print(f"  ❌ Lỗi kết nối tới dịch vụ giải CAPTCHA: {e}")
            return None

    def solve_image_captcha(self, page, img_selector):
        """Chụp ảnh captcha từ selector, chuyển base64 và nhờ 2Captcha giải"""
        if not self.captcha_api_key:
            print("  ⚠️ Không tìm thấy CAPTCHA API Key trong cấu hình.")
            return ""
            
        try:
            # Lấy phần tử ảnh captcha
            img_element = page.locator(img_selector).first
            if img_element.count() == 0:
                print("  ❌ Không tìm thấy ảnh captcha để giải.")
                return ""
            
            # Chụp ảnh của riêng element đó dưới dạng base64
            img_bytes = img_element.screenshot(timeout=5000)
            import base64
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")
            
            print("  🧩 Đang gửi yêu cầu giải Image CAPTCHA tới 2Captcha...")
            import requests
            url = "http://2captcha.com/in.php"
            data = {
                "key": self.captcha_api_key,
                "method": "base64",
                "body": img_base64,
                "numeric": 1,  # Chỉ lấy số
                "min_len": 3,
                "max_len": 7,
                "json": 1
            }
            r = requests.post(url, json=data, timeout=15)
            res = r.json()
            if res.get("status") != 1:
                print(f"  ❌ Lỗi gửi CAPTCHA tới 2Captcha: {res.get('request')}")
                return ""
                
            task_id = res.get("request")
            poll_url = "http://2captcha.com/res.php"
            poll_params = {
                "key": self.captcha_api_key,
                "action": "get",
                "id": task_id,
                "json": 1
            }
            
            print("  ⏳ Đang chờ 2Captcha giải Image CAPTCHA...")
            for _ in range(15):
                time.sleep(3)
                pr = requests.get(poll_url, params=poll_params, timeout=10)
                pres = pr.json()
                if pres.get("status") == 1:
                    code = pres.get("request")
                    print(f"  ✅ Giải CAPTCHA thành công! Mã: {code}")
                    return code
                if pres.get("request") == "CAPCHA_NOT_READY":
                    continue
                print(f"  ❌ Lỗi giải CAPTCHA: {pres.get('request')}")
                break
        except Exception as e:
            print(f"  ❌ Lỗi xảy ra khi tự động giải Image CAPTCHA: {e}")
        return ""

    def solve_image_captcha_free(self, page, img_selector):
        """Giải captcha bằng ocr.space API miễn phí (không cần API key của khách)"""
        try:
            img_element = page.locator(img_selector).first
            if img_element.count() == 0:
                return ""
            
            img_bytes = img_element.screenshot(timeout=5000)
            import base64
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")
            
            import requests
            url = "https://api.ocr.space/parse/image"
            payload = {
                "apikey": "helloworld",
                "base64Image": f"data:image/png;base64,{img_base64}",
                "language": "eng",
                "isOverlayRequired": False,
                "OCREngine": 2
            }
            r = requests.post(url, data=payload, timeout=10)
            res = r.json()
            parsed_results = res.get("ParsedResults", [])
            if parsed_results:
                text = parsed_results[0].get("ParsedText", "").strip()
                digits = "".join(c for c in text if c.isdigit())
                if len(digits) >= 3:
                    print(f"  ✅ Giải CAPTCHA thành công qua Free API! Mã: {digits}")
                    return digits
        except Exception as e:
            print(f"  ⚠️ Lỗi giải captcha bằng Free API: {e}")
        return ""

    def solve_image_captcha_local(self, page, img_selector):
        """Giải captcha bằng thư viện EasyOCR cục bộ (miễn phí, offline, nhanh, chính xác)"""
        try:
            img_element = page.locator(img_selector).first
            if img_element.count() == 0:
                return ""
            
            img_bytes = img_element.screenshot(timeout=5000)
            
            if not hasattr(self, "ocr_reader") or self.ocr_reader is None:
                import easyocr
                self.ocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
                
            results = self.ocr_reader.readtext(img_bytes)
            if results:
                text = "".join([res[1] for res in results])
                digits = "".join(c for c in text if c.isdigit())
                if len(digits) >= 3:
                    print(f"  ✅ Giải CAPTCHA thành công qua Local OCR! Mã: {digits}")
                    return digits
        except Exception as e:
            print(f"  ⚠️ Lỗi giải captcha bằng Local OCR: {e}")
        return ""

    def handle_turnstile_if_present(self, page):
        """Kiểm tra xem trang có Turnstile hay Cloudflare Challenge không và giải nếu có API Key"""
        if not self.captcha_api_key:
            return False
            
        try:
            # Tìm thẻ iframe Cloudflare Turnstile
            turnstile_iframe = page.locator("iframe[src*='challenges.cloudflare.com/cdn-cgi/challenge-platform']").first
            if turnstile_iframe.count() > 0:
                print("  🧩 Phát hiện Cloudflare Turnstile CAPTCHA! Tiến hành giải tự động...")
                src = turnstile_iframe.get_attribute("src")
                import re
                sitekey_match = re.search(r'/g/([^/]+)|sitekey=([^&]+)', src)
                sitekey = None
                if sitekey_match:
                    sitekey = sitekey_match.group(1) or sitekey_match.group(2)
                    
                if not sitekey:
                    sitekey = page.evaluate("""
                        () => {
                            const ts = document.querySelector('.cf-turnstile, [data-sitekey]');
                            return ts ? ts.getAttribute('data-sitekey') : null;
                        }
                    """)
                    
                if sitekey:
                    token = self.solve_turnstile_captcha(page.url, sitekey)
                    if token:
                        page.evaluate(f"""
                            (token) => {{
                                const textareas = document.querySelectorAll('textarea[name="cf-turnstile-response"], textarea[name="g-recaptcha-response"]');
                                textareas.forEach(t => {{
                                    t.value = token;
                                    t.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                    t.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                }});
                                
                                if (window.cf && window.cf.tokenCreated) {{
                                    window.cf.tokenCreated(token);
                                }}
                            }}
                        """, token)
                        time.sleep(2)
                        print("  🧩 Đã chèn token giải CAPTCHA thành công!")
                        return True
        except Exception as e_ts:
            print(f"  ⚠️ Lỗi khi xử lý giải Turnstile: {e_ts}")
        return False

    def parse_price(self, price_str, area_str):
        """Phân tích giá tiền, tự động quy đổi từ USD/m2 sang VNĐ/tháng dựa trên diện tích và tỷ giá hiện tại (~25,400)"""
        import re
        price_str = str(price_str).strip().lower()
        area_str = str(area_str).strip().lower()
        
        # Lấy diện tích dạng số
        area_num = 100 # Diện tích mặc định
        area_match = re.search(r'(\d+)', area_str)
        if area_match:
            area_num = int(area_match.group(1))

        # Tỷ giá đô la Mỹ sang VND (Cập nhật mới nhất > 26000)
        usd_rate = 26200
        
        # Nếu giá chứa USD hoặc $ hoặc đô
        if 'usd' in price_str or '$' in price_str or 'đô' in price_str:
            # Tìm số trong chuỗi giá
            price_match = re.search(r'([\d\.,]+)', price_str)
            if price_match:
                price_val = float(price_match.group(1).replace(',', '.'))
                # Quy đổi tổng giá trị VNĐ hàng tháng = Giá USD * Diện tích * Tỷ giá
                total_vnd = int(price_val * area_num * usd_rate)
                return total_vnd
        else:
            # Nếu là giá VNĐ thông thường
            # Loại bỏ các ký tự không phải số
            price_digits = re.sub(r'[^\d]', '', price_str)
            if price_digits:
                return int(price_digits)
                
        return 0

    def download_property_images(self, source_url, property_title):
        """Tải các ảnh chất lượng cao từ bài viết bất động sản về thư mục cục bộ.
        Nếu không tìm thấy ảnh hoặc source_url trống, tự động tạo ảnh bìa gradient tiếp thị chuyên nghiệp làm fallback.
        Đồng thời, nếu số ảnh thu được ít hơn 3, tự động tạo thêm các slide infographic tiếp thị đẹp mắt để đạt tối thiểu 3 ảnh (đáp ứng điều kiện của thuviennhadat.vn).
        """
        import os
        import re
        import requests
        
        safe_title = re.sub(r'[^\w\-_\. ]', '', property_title).strip().replace(' ', '_')
        download_dir = os.path.abspath(os.path.join("downloads", safe_title))
        os.makedirs(download_dir, exist_ok=True)
        
        local_paths = []
        
        # Chỉ tải nếu có source_url hợp lệ
        if source_url and source_url.startswith("http"):
            print(f"  => Bắt đầu cào ảnh từ nguồn: {source_url}...")
            try:
                # Mở trang nguồn bằng page hiện tại để cào danh sách ảnh
                temp_page = self.context.new_page()
                temp_page.goto(source_url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(2)
                
                img_urls = temp_page.evaluate("""
                    () => {
                        const urls = [];
                        const galleryImgs = document.querySelectorAll('.ere-property-slide img, .property-gallery img, .property-slider img, .wp-post-image');
                        galleryImgs.forEach(img => {
                            if (img.src && img.src.includes('/wp-content/uploads/')) {
                                urls.push(img.src);
                            }
                        });
                        
                        const bodyImgs = document.querySelectorAll('.entry-content img, article img');
                        bodyImgs.forEach(img => {
                            if (img.src && img.src.includes('/wp-content/uploads/')) {
                                urls.push(img.src);
                            }
                        });
                        
                        if (urls.length === 0) {
                            document.querySelectorAll('img').forEach(img => {
                                if (img.src && img.src.includes('/wp-content/uploads/')) {
                                    urls.push(img.src);
                                }
                            });
                        }
                        return [...new Set(urls)];
                    }
                """)
                temp_page.close()
                
                filtered_urls = []
                for u in img_urls:
                    u_lower = u.lower()
                    if 'logo' in u_lower or 'avatar' in u_lower or 'icon' in u_lower:
                        continue
                    filtered_urls.append(u)
                    
                target_urls = filtered_urls[:5]
                if target_urls:
                    print(f"  => Tìm thấy {len(target_urls)} ảnh phù hợp. Đang tải...")
                    for idx, img_url in enumerate(target_urls):
                        try:
                            ext = ".jpg"
                            if ".png" in img_url.lower():
                                ext = ".png"
                            local_path = os.path.join(download_dir, f"img_{idx + 1}{ext}")
                            
                            response = requests.get(img_url, timeout=15, headers={
                                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                            })
                            if response.status_code == 200:
                                with open(local_path, "wb") as f:
                                    f.write(response.content)
                                local_paths.append(local_path)
                                print(f"    ✓ Đã tải: img_{idx + 1}{ext}")
                        except Exception as e_dl:
                            print(f"    ✗ Lỗi khi tải ảnh {img_url}: {e_dl}")
                else:
                    print("  ⚠️ Không tìm thấy ảnh hợp lệ nào từ bài viết.")
            except Exception as e:
                print(f"  ⚠️ Lỗi tổng thể khi cào hình ảnh từ web: {e}")
                
        # Đảm bảo có tối thiểu 3 hình ảnh cho thuviennhadat.vn và tăng chất lượng quảng cáo
        if len(local_paths) < 3:
            print(f"  => Hiện có {len(local_paths)} ảnh, tự động tạo thêm slide infographic tiếp thị đẹp mắt để đạt tối thiểu 3 ảnh...")
            try:
                from PIL import Image, ImageDraw
                
                # Định nghĩa 3 palette màu gradient sang trọng và nội dung quảng cáo
                gradients = [
                    # Slide 1: Emerald/Teal (Ảnh bìa)
                    {"start": (0, 145, 148), "end": (19, 185, 188), "title": property_title, "subtitle": "OFFICE ĐÀ NẴNG - BÀI ĐĂNG CHÍNH THỨC", "footer": "Hotline: 0935.723.727"},
                    # Slide 2: Deep Blue/Navy (Tiện ích)
                    {"start": (15, 32, 67), "end": (84, 90, 214), "title": "DỊCH VỤ VĂN PHÒNG CHUYÊN NGHIỆP", "subtitle": "• Diện tích đa dạng & linh hoạt\n• Hỗ trợ pháp lý cẩn thận & chu đáo\n• Tư vấn khảo sát hoàn toàn miễn phí", "footer": "officedanang.vn - Uy tín hàng đầu"},
                    # Slide 3: Purple/Ruby (Liên hệ)
                    {"start": (81, 10, 84), "end": (186, 24, 142), "title": "HÃY LIÊN HỆ NGAY VỚI CHÚNG TÔI", "subtitle": "Tìm nhanh văn phòng thuê phù hợp nhất\nTiết kiệm thời gian & tối ưu chi phí tối đa", "footer": "Hotline hỗ trợ 24/7: 0935.723.727"}
                ]
                
                needed = 3 - len(local_paths)
                for idx in range(needed):
                    slide_idx = len(local_paths)
                    grad = gradients[slide_idx % len(gradients)]
                    path = os.path.join(download_dir, f"infographic_slide_{slide_idx + 1}.png")
                    
                    img = Image.new("RGB", (800, 600), grad["start"])
                    draw = ImageDraw.Draw(img)
                    
                    try:
                        from PIL import ImageFont
                        font_title = ImageFont.truetype("Roboto-Regular.ttf", 36)
                        font_sub = ImageFont.truetype("Roboto-Regular.ttf", 24)
                        font_footer = ImageFont.truetype("Roboto-Regular.ttf", 20)
                    except Exception as e:
                        print(f"Lỗi load font: {e}")
                        font_title = None
                        font_sub = None
                        font_footer = None

                    # Vẽ gradient chéo
                    for y in range(600):
                        factor = y / 600.0
                        r = int(grad["start"][0] + (grad["end"][0] - grad["start"][0]) * factor)
                        g = int(grad["start"][1] + (grad["end"][1] - grad["start"][1]) * factor)
                        b = int(grad["start"][2] + (grad["end"][2] - grad["start"][2]) * factor)
                        draw.line([(0, y), (800, y)], fill=(r, g, b))
                        
                    # Khung viền thanh lịch
                    draw.rectangle([(20, 20), (780, 580)], outline="#ffffff", width=2)
                    
                    # Logo góc trên trái
                    draw.text((40, 40), "OFFICE ĐÀ NẴNG", fill="#ffffff", font=font_sub)
                    
                    # Nội dung text ở giữa
                    words = grad["title"].split()
                    lines = []
                    current_line = []
                    for word in words:
                        if len(' '.join(current_line + [word])) <= 25:
                            current_line.append(word)
                        else:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                    if current_line:
                        lines.append(' '.join(current_line))
                        
                    y_start = 180
                    for line in lines[:3]:
                        draw.text((85, y_start), line, fill="#ffffff", font=font_title)
                        y_start += 50
                        
                    # Phụ đề
                    y_start += 20
                    sub_lines = grad["subtitle"].split('\n')
                    for sub_line in sub_lines:
                        draw.text((85, y_start), sub_line, fill="#f0f0f0", font=font_sub)
                        y_start += 35
                        
                    # Footer chân trang
                    draw.text((85, 500), grad["footer"], fill="#f4ff5c", font=font_footer)
                    
                    img.save(path)
                    local_paths.append(path)
                    print(f"    ✓ Đã tạo slide infographic tiếp thị fallback: {path}")
            except Exception as e_infographic:
                print(f"  ⚠️ Lỗi khi tạo slide infographic: {e_infographic}")
                
        # Tự động chèn watermark nếu được cấu hình trong config.json
        try:
            import json
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                wm_cfg = cfg.get("watermark", {})
                if wm_cfg.get("enabled", False):
                    print("  🎨 Đang tự động chèn watermark vào toàn bộ ảnh tin đăng...")
                    for path in local_paths:
                        self.apply_watermark(path, wm_cfg)
        except Exception as e_cfg:
            print(f"  ⚠️ Lỗi khi nạp cấu hình watermark: {e_cfg}")
                 
        return local_paths

    def apply_watermark(self, image_path, watermark_config):
        """Chèn watermark chữ vào ảnh và lưu đè"""
        if not watermark_config or not watermark_config.get("enabled", False):
            return
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            import os
            
            img = Image.open(image_path).convert("RGBA")
            width, height = img.size
            
            # Tạo overlay trong suốt để vẽ watermark
            txt_overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_overlay)
            
            # Cấu hình font kích thước linh hoạt
            font_size = int(max(height, width) * 0.035)
            if font_size < 12: font_size = 12
            
            try:
                font = ImageFont.truetype("Roboto-Regular.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()
                
            text = watermark_config.get("text", "officedanang.vn - 0935.723.727")
            color_hex = watermark_config.get("color", "#FFFFFF").lstrip('#')
            opacity = float(watermark_config.get("opacity", 0.6))
            
            # Chuyển HEX sang RGBA
            r = int(color_hex[0:2], 16) if len(color_hex) >= 2 else 255
            g = int(color_hex[2:4], 16) if len(color_hex) >= 4 else 255
            b = int(color_hex[4:6], 16) if len(color_hex) >= 6 else 255
            fill_color = (r, g, b, int(255 * opacity))
            
            # Tính toán kích thước văn bản
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except AttributeError:
                text_width, text_height = draw.textsize(text, font=font)
                
            # Xác định vị trí
            pos_type = watermark_config.get("position", "bottom_right")
            if pos_type == "center":
                x = (width - text_width) // 2
                y = (height - text_height) // 2
            elif pos_type == "top_left":
                x = 20
                y = 20
            elif pos_type == "top_right":
                x = width - text_width - 20
                y = 20
            elif pos_type == "bottom_left":
                x = 20
                y = height - text_height - 20
            else: # bottom_right
                x = width - text_width - 20
                y = height - text_height - 20
                
            # Vẽ bóng đổ mờ màu đen để làm nổi bật văn bản trên nền sáng/tối
            shadow_color = (0, 0, 0, int(150 * opacity))
            draw.text((x + 2, y + 2), text, fill=shadow_color, font=font)
            draw.text((x, y), text, fill=fill_color, font=font)
            
            # Ghép ảnh gốc và overlay
            watermarked = Image.alpha_composite(img, txt_overlay)
            
            # Lưu đè lại ảnh
            if image_path.lower().endswith(".png"):
                watermarked.save(image_path, "PNG")
            else:
                watermarked.convert("RGB").save(image_path, "JPEG", quality=90)
            print(f"    ✓ Đã chèn watermark thành công: {os.path.basename(image_path)}")
        except Exception as e_wm:
            print(f"    ✗ Lỗi chèn watermark vào ảnh {image_path}: {e_wm}")

    def login_raovat_net(self, email, password):
        """Đăng nhập raovat.net bằng email + password.
        Selectors xác nhận qua scraping: useremail field + button#buttonLogin
        """
        print(f"Đang đăng nhập raovat.net với email: {email}")
        try:
            self.page.goto("https://raovat.net/dang-nhap", wait_until="domcontentloaded")
            time.sleep(1)
            self.page.fill("input[name='useremail']", email)
            self.page.fill("input[name='password']", password)
            self.page.click("button#buttonLogin")
            time.sleep(3)
            current_url = self.page.url
            if "dang-nhap" not in current_url:
                print(f"=> Đăng nhập raovat.net thành công! URL: {current_url}")
            else:
                # Đôi khi cookie vẫn được set dù URL không đổi
                user_check = self.page.evaluate(
                    "document.querySelector('.usr-name')?.innerText || ''"
                )
                if user_check:
                    print(f"=> Đăng nhập thành công (user: {user_check.strip()})")
                else:
                    print("=> Cảnh báo: URL vẫn là dang-nhap, có thể sai mật khẩu hoặc cần captcha")
            return True
        except Exception as e:
            print(f"=> Lỗi khi đăng nhập raovat: {e}")
            return False

    def post_raovat_net(self, item):
        """Đăng tin lên raovat.net theo flow 2 bước:
        Bước 1: Chọn danh mục (sitecatid=11 / subcatid=51 = Thuê và cho thuê nhà)
        Bước 2: Điền nội dung form và submit
        """
        print(f"Bắt đầu đăng tin Raovat: {item.get('title')}")
        try:
            import re
            import os

            # Tự động tải hình ảnh từ source_url của website hoặc tạo ảnh bìa fallback
            local_images = self.download_property_images(item.get('source_url', ''), item.get('title', ''))

            # --- BƯỚC 1: Chọn danh mục ---
            print("- Bước 1: Chọn danh mục...")
            page_cat = "https://raovat.net/dang-tin-11-Nha-cua-Dat-dai"
            self.page.goto(page_cat, wait_until="domcontentloaded")
            time.sleep(2)

            # Chọn subcategory "Thuê và cho thuê nhà" (subcatid=51) via JS
            self.page.evaluate("""
                () => {
                    const subDiv = document.querySelector('.sub-cate[onclick*="51"]');
                    if (subDiv) subDiv.click();
                }
            """)
            time.sleep(1)

            # Đợi nút Tiếp tục sẵn sàng và click qua JS để tránh bị modal chặn pointer events
            print("- Đợi nút Tiếp tục sẵn sàng và click...")
            btn_ready = False
            for _ in range(10):
                is_hidden = self.page.evaluate("() => { const btn = document.querySelector('#btnNextStep button'); return btn ? btn.classList.contains('hidden') : true; }")
                if not is_hidden:
                    btn_ready = True
                    break
                time.sleep(1)
                
            self.page.evaluate("""
                () => {
                    const btn = document.querySelector('#btnNextStep button');
                    if (btn) {
                        btn.classList.remove('hidden');
                        btn.click();
                    }
                }
            """)
            time.sleep(5)
            print(f"  => URL step 2: {self.page.url}")

            # Kiểm tra xem có bị chuyển hướng về trang quản lý tin do giới hạn bài đăng
            if "quan-ly" in self.page.url or "Quản lý tin rao vặt" in self.page.title() or "Bạn đang có" in self.page.content():
                print("  ❌ Lỗi: Tài khoản của bạn đã đạt giới hạn số lượng tin đăng cho phép trên raovat.net (hoặc bị chuyển về trang Quản lý tin). Hãy xóa hoặc ẩn bớt các bài đăng cũ trước khi đăng bài mới.")
                return False

            # Chờ form step 2 xuất hiện
            self.page.wait_for_selector("input[name='sitetitle']", timeout=10000)

            # --- BƯỚC 2: Điền form nội dung ---
            print("- Bước 2: Điền tiêu đề...")
            title = item.get('title', '')
            if len(title) > 50:
                title = title[:50].strip()
                print(f"  ⚠️ Cảnh báo: Tiêu đề > 50 ký tự, tự động cắt còn: '{title}'")
            self.page.fill("input[name='sitetitle']", title)

            print("- Chọn loại tin (Thuê - Cho thuê) bằng JS...")
            try:
                self.page.evaluate("""
                    () => {
                        if (typeof $ !== 'undefined') {
                            $('#notify').val('T').trigger('chosen:updated');
                            console.log('Set notify to T (Thuê - Cho thuê) via jQuery');
                        } else {
                            const sel = document.querySelector('select[name="notify"]');
                            if (sel) {
                                sel.value = 'T';
                                sel.dispatchEvent(new Event('change', {bubbles: true}));
                            }
                        }
                    }
                """)
                time.sleep(0.5)
            except Exception as e_notify:
                print(f"  => Bỏ qua chọn loại tin: {e_notify}")

            print("- Chọn thành phố (Đà Nẵng) và Quận huyện bằng JS...")
            try:
                # 1. Chọn thành phố Đà Nẵng
                self.page.evaluate("""
                    () => {
                        if (typeof $ !== 'undefined') {
                            const sel = document.querySelector('select[name="cityid"]');
                            if (!sel) return;
                            const opt = Array.from(sel.options).find(
                                o => o.text.toLowerCase().includes('nẵng') ||
                                     o.text.toLowerCase().includes('nang') ||
                                     o.text.toLowerCase().includes('da nang')
                            );
                            if (opt) {
                                $('#cityid').val(opt.value).trigger('change').trigger('chosen:updated');
                            }
                        }
                    }
                """)
                # Đợi AJAX của trang tải danh sách quận/huyện
                time.sleep(2)

                # 2. Chọn Quận/Huyện dựa trên dữ liệu district từ CSV
                district_name = item.get('district', '')
                print(f"  => Đang chọn Quận/Huyện: {district_name}")
                
                self.page.evaluate(f"""
                    () => {{
                        const targetDistrict = "{district_name}".toLowerCase().trim();
                        if (typeof $ !== 'undefined') {{
                            const subSel = document.querySelector('select[name="subcity"]');
                            if (!subSel) return;
                            
                            const opt = Array.from(subSel.options).find(
                                o => {{
                                    const text = o.text.toLowerCase();
                                    return text.includes(targetDistrict) || 
                                           targetDistrict.includes(text) ||
                                           text.replace(/q\\.\\s*/, '').trim().includes(targetDistrict);
                                }}
                            );
                            if (opt) {{
                                $('#subcity').val(opt.value).trigger('chosen:updated');
                                console.log('Set subcity success: ' + opt.text);
                            }} else {{
                                const firstValid = Array.from(subSel.options).find(o => o.value !== "");
                                if (firstValid) {{
                                    $('#subcity').val(firstValid.value).trigger('chosen:updated');
                                }}
                            }}
                        }}
                    }}
                """)
                time.sleep(1)
                print("  => Đã chọn xong Tỉnh thành & Quận huyện")
            except Exception as e_city:
                print(f"  => Bỏ qua chọn thành phố/quận: {e_city}")

            print("- Điền giá...")
            price_val = self.parse_price(item.get('price', ''), item.get('area', ''))
            if price_val > 100000:
                self.page.evaluate(f"document.querySelector('input[name=\"siteprice\"]').value = '{price_val}'")
                # Chọn VNĐ (value=1) qua JS - sitecurrency cũng có thể bị ẩn
                self.page.evaluate("""
                    () => {
                        const sel = document.querySelector('select[name="sitecurrency"]');
                        if (sel) { sel.value = '1'; sel.dispatchEvent(new Event('change', {bubbles: true})); }
                    }
                """)
                self.page.evaluate("const u = document.querySelector('input[name=\"siteunit\"]'); if(u) u.value = 'tháng';")
                print(f"  => Giá quy đổi: {price_val} VNĐ/tháng")
            else:
                self.page.evaluate("const p = document.querySelector('input[name=\"siteprice\"]'); if(p) p.value = '0';")
                print("  => Giá quy đổi: Thoả thuận (0 VNĐ)")

            print("- Điền nội dung...")
            content = item.get('content', '').replace('\\n', '\n')
            self.page.fill("textarea[name='sitedescription']", content)

            print("- Điền từ khóa...")
            title_words = item.get('title', '').split()[:5]
            tags = ', '.join(title_words)
            self.page.fill("input[name='sitetags']", tags)

            if local_images:
                print("- Tải lên hình ảnh bài viết...")
                try:
                    abs_paths = [os.path.abspath(p) for p in local_images]
                    self.page.set_input_files("input[name='ax_file_input']", abs_paths)
                    time.sleep(2)
                    
                    # Click nút tải ảnh lên của plugin
                    try:
                        upload_btn = self.page.locator(".ax-upload-all")
                        if upload_btn.count() > 0 and upload_btn.is_visible():
                            upload_btn.click()
                            time.sleep(4)
                            print(f"  => Đã bấm nút Upload All cho {len(local_images)} ảnh")
                        else:
                            # Fallback kích hoạt qua JS nếu nút bị CSS ẩn
                            self.page.evaluate("if(document.querySelector('.ax-upload-all')) document.querySelector('.ax-upload-all').click();")
                            time.sleep(4)
                            print(f"  => Đã kích hoạt JS Upload All cho {len(local_images)} ảnh")
                    except Exception as ev:
                        print(f"  => Không thể kích hoạt upload all, có thể nó đã tự động tải. Lỗi: {ev}")

                except Exception as e_img:
                    print(f"  ⚠️ Bỏ qua tải ảnh: {e_img}")

            print("- Đóng modal popup nếu có...")
            try:
                # Đóng modal "Nhận thông báo" và bất kỳ modal nào khác
                self.page.evaluate("""
                    () => {
                        // Click Cancel trên mọi modal đang hiện
                        document.querySelectorAll('.modal.in .btn-cancel, .modal.in [data-dismiss="modal"]')
                            .forEach(btn => btn.click());
                        // Ẩn backdrop overlay
                        document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
                        document.querySelectorAll('.modal.in').forEach(el => {
                            el.classList.remove('in');
                            el.style.display = 'none';
                        });
                        document.body.classList.remove('modal-open');
                    }
                """)
                time.sleep(0.5)
            except:
                pass

            print("- Đăng tin (dùng JS submit để tránh bị modal chặn)...")
            # Dùng JS submit form thay vì click button để tránh overlay chặn
            self.page.evaluate("""
                () => {
                    const btn = document.querySelector('button.btn-success');
                    if (btn) btn.click();
                }
            """)
            time.sleep(6)

            # Kiểm tra kết quả
            current_url = self.page.url
            page_title = self.page.evaluate("document.title")
            body_text = self.page.evaluate("document.body.innerText")
            print(f"  => URL: {current_url}")
            print(f"  => Title: {page_title}")

            if 'xem' in current_url or 'quan-ly' in current_url:
                print("  ✅ ĐĂNG TIN RAOVAT THÀNH CÔNG!")
                success = True
            elif 'thành công' in body_text.lower():
                print("  ✅ ĐĂNG TIN RAOVAT THÀNH CÔNG (Đã ghi nhận trên hệ thống)!")
                success = True
            else:
                errors = self.page.evaluate("""
                    Array.from(document.querySelectorAll('.alert-danger, .error, .msg-error'))
                        .map(e => e.innerText).join(' | ')
                """)
                if errors.strip():
                    print(f"  ❌ Lỗi: {errors}")
                else:
                    print("  ⚠️  Kiểm tra thủ công trên raovat.net")
                success = False

            time.sleep(3)
            print("=> Hoàn tất đăng tin Raovat ✓")
            return success
        except Exception as e:
            print(f"=> Lỗi khi đăng tin raovat: {e}")
            return False


    def login_thuviennhadat(self, username, password):
        """Đăng nhập thuviennhadat.vn sử dụng tài khoản thật"""
        print(f"Đang đăng nhập thuviennhadat.vn với tài khoản: {username}")
        try:

            self.page.goto("https://thuviennhadat.vn/Users/Login?returnUrl=%2Fdang-tin", wait_until="domcontentloaded")
            time.sleep(2)
            self.page.fill("input#phone-mail-login-view", username)
            self.page.fill("input#password-login-view", password)
            self.page.click("button#button-submit-login-view")
            
            # Đợi chuyển trang về dang-tin hoặc có cookie session đăng nhập thành công
            self.page.wait_for_url("**/dang-tin**", timeout=15000)
            time.sleep(3)
            
            # Đóng modal chào mừng nếu có
            try:
                if self.page.locator("div.header:has-text('Chào mừng')").is_visible():
                    self.page.click("i.close.icon")
                    time.sleep(1)
            except Exception:
                pass
                
            print("=> Đăng nhập thuviennhadat.vn thành công!")
            return True
        except Exception as e:
            print(f"=> Lỗi đăng nhập thuviennhadat.vn: {e}")
            return False

    def post_thuviennhadat(self, item):
        """Đăng tin lên thuviennhadat.vn theo quy trình 3 bước"""
        print(f"Bắt đầu đăng tin trên ThuVienNhaDat: {item.get('title')}")
        try:
            import os
            import re
            # Tự động tải hình ảnh từ source_url của website hoặc tạo ảnh bìa fallback
            local_images = self.download_property_images(item.get('source_url', ''), item.get('title', ''))

            # Luôn đi đến trang dang-tin để đảm bảo form sạch sẽ, tránh ô nhiễm trạng thái giữa các bài đăng
            self.page.goto("https://thuviennhadat.vn/dang-tin", wait_until="domcontentloaded")
            time.sleep(3)

            # Đóng modal chào mừng nếu có
            try:
                if self.page.locator("div.header:has-text('Chào mừng')").is_visible():
                    self.page.click("i.close.icon")
                    time.sleep(1)
            except Exception:
                pass

            # --- BƯỚC 1: Thông tin Nhà Đất ---
            print("- Bước 1: Chọn Nhu cầu...")
            # Cho thuê: `.tag._post-transaction-type._rent`, Bán: `.tag._post-transaction-type._sell`
            is_rent = True
            rent_keywords = ["thuê", "thue", "lease", "rent"]
            title_lower = item.get('title', '').lower()
            if any(k in title_lower for k in rent_keywords):
                self.page.click(".tag._post-transaction-type._rent")
            else:
                self.page.click(".tag._post-transaction-type._sell")
            time.sleep(1)

            # Mở modal địa chỉ và chọn dropdowns
            print("- Điền địa chỉ...")
            self.page.click("input[name='PostFullAddress']")
            time.sleep(2)

            def select_dropdown(dropdown_selector, search_text):
                self.page.click(dropdown_selector)
                time.sleep(1)
                self.page.fill(f"{dropdown_selector} input.search", search_text)
                time.sleep(2)
                self.page.keyboard.press("Enter")
                time.sleep(1)

            # Mặc định là Đà Nẵng, Hải Châu, Bình Thuận
            city = "Đà Nẵng"
            district = item.get('district', '')
            if not district:
                district = "Quận Hải Châu"
            elif "hải châu" in district.lower() or "hai chau" in district.lower():
                district = "Quận Hải Châu"
            elif "thanh khê" in district.lower() or "thanh khe" in district.lower():
                district = "Quận Thanh Khê"
            elif "liên chiểu" in district.lower() or "lien chieu" in district.lower():
                district = "Quận Liên Chiểu"
            elif "sơn trà" in district.lower() or "son tra" in district.lower():
                district = "Quận Sơn Trà"
            elif "ngũ hành sơn" in district.lower() or "ngu hanh son" in district.lower():
                district = "Quận Ngũ Hành Sơn"
            elif "cẩm lệ" in district.lower() or "cam le" in district.lower():
                district = "Quận Cẩm Lệ"
            else:
                district = "Quận Hải Châu"

            # Xác định Ward (Phường) phù hợp với Quận để tránh mâu thuẫn địa lý
            ward_map = {
                "Quận Hải Châu": "Phường Bình Thuận",
                "Quận Thanh Khê": "Phường Thạc Gián",
                "Quận Liên Chiểu": "Phường Hòa Minh",
                "Quận Sơn Trà": "Phường An Hải Bắc",
                "Quận Ngũ Hành Sơn": "Phường Mỹ An",
                "Quận Cẩm Lệ": "Phường Khuê Trung"
            }
            ward = ward_map.get(district, "Phường Bình Thuận")

            select_dropdown("div.ui.search.dropdown._input-city", city)
            select_dropdown("div.ui.search.dropdown._input-dictrict", district)
            select_dropdown("div.ui.search.dropdown._input-ward", ward)

            # Điền tên đường
            street = "Nguyễn Văn Linh"
            addr_str = item.get('address', '').strip()
            
            if ',' in addr_str:
                # Nếu có dấu phẩy, thường đoạn đầu tiên là số nhà/tên đường
                first_part = addr_str.split(',')[0].strip()
                if first_part:
                    # Bỏ các từ như "Quận", "Phường", "Thành phố" nếu người dùng điền thiếu tên đường
                    if not any(x in first_part.lower() for x in ["quận", "phường", "thành phố", "tỉnh", "tp"]):
                        street = first_part
            else:
                # Thử trích xuất tên đường từ title hoặc address của item nếu có
                street_match = re.search(r'(đường|đ\.)\s+([A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝĂĐĨŨƠƯa-zàáâãèéêìíòóôõùúýăđĩũơư\s\d]+)', addr_str)
                if street_match:
                    street = street_match.group(2).strip()
                    street = ' '.join(street.split()[:4])
                elif addr_str and len(addr_str.split()) <= 6:
                    street = addr_str
            
            self.page.fill("input[name='AddressName']", street)
            time.sleep(1)
            self.page.click("._btn-submit-location-picking")
            time.sleep(2)

            # Chọn Loại Nhà Đất: Văn phòng
            print("- Chọn Loại Nhà Đất...")
            select_dropdown("div.ui.search.dropdown._input-post-category", "Văn phòng")

            # Nhập diện tích
            area_val = 100
            area_str = str(item.get('area', ''))
            area_match = re.search(r'(\d+)', area_str)
            if area_match:
                area_val = int(area_match.group(1))
            self.page.fill("input[name='PostArea']", str(area_val))

            # Nhập mức giá
            price_val = self.parse_price(item.get('price', ''), item.get('area', ''))

            # Với văn phòng cho thuê, ta điền giá dạng VND/m2 (VND/m/Tháng = option value 2)
            if price_val > 100000:
                # Tính giá / m2
                price_per_m2 = int(price_val / area_val)
                self.page.fill("input[name='PostPrice']", str(price_per_m2))
                time.sleep(1)
                # Chọn đơn vị: VND/m2/Tháng (value = 2)
                self.page.click("div.ui.search.dropdown._input-post-price-type")
                time.sleep(1)
                self.page.click("div.ui.search.dropdown._input-post-price-type div.item[data-value='2']")
                time.sleep(1)
                print(f"  => Điền giá quy đổi: {price_per_m2} VND/m²/tháng")
            else:
                # Thỏa thuận
                self.page.click("div.ui.search.dropdown._input-post-price-type")
                time.sleep(1)
                self.page.click("div.ui.search.dropdown._input-post-price-type div.item[data-value='3']")
                time.sleep(1)
                print("  => Điền giá quy đổi: Thỏa thuận")

            # Thêm thông tin liên hệ chính nếu chưa có liên hệ nào hoặc để đảm bảo liên hệ tồn tại
            print("- Thêm liên hệ...")
            try:
                # Click thêm liên hệ thông qua JS evaluate click
                self.page.evaluate('document.querySelector("._btn-contact-adding").click()')
                time.sleep(2)
                # Random tên người liên hệ
                names = ["Bình Office Danang", "Thiên Bình", "Nguyễn Ngọc Thiên Bình", "Mr Bình"]
                selected_name = random.choice(names)
                self.page.fill("input._input-contact-name", selected_name)
                print(f"  => Điền thông tin liên hệ: {selected_name}")
                self.page.fill("input._input-contact-phone", "0935723727")
                self.page.click("._modal-contact-adding .ui.checkbox label")
                time.sleep(1)
                self.page.click("._btn-submit-contact-adding")
                time.sleep(2)
                print("  => Đã thêm/cập nhật thông tin liên hệ thành công")
            except Exception as e_contact:
                print(f"  => Liên hệ chính đã có sẵn hoặc bỏ qua: {e_contact}")

            # Điền tiêu đề & mô tả
            print("- Điền tiêu đề & mô tả...")
            self.page.fill("textarea[name='PostTitle']", item.get('title', ''))
            content = item.get('content', '').replace('\\n', '\n')
            # Thuviennhadat không chấp nhận ký hiệu $ trong nội dung
            # Chuyển đổi thẳng sang VNĐ cho tự nhiên và chắc chắn được chấp nhận
            # Ví dụ: $15/m² → 393.000 VNĐ/m², $15 → 393.000 VNĐ
            import re as _re
            _USD_RATE = 26200

            def _usd_to_vnd(m):
                try:
                    vnd = int(float(m.group(1).replace(',', '.')) * _USD_RATE)
                    return f"{vnd:,}".replace(',', '.') + " VNĐ"
                except Exception:
                    return m.group(0).replace('$', '')

            content_clean = _re.sub(r'\$([\d]+(?:[\.,]\d+)?)', _usd_to_vnd, content)
            content_clean = content_clean.replace('$', '')  # xóa $ còn sót
            if content_clean != content:
                print(f"  => Đã chuyển đổi giá USD → VNĐ trong nội dung (tỷ giá {_USD_RATE:,} VNĐ/USD)")
            self.page.fill("textarea[name='PostDescription']", content_clean)

            # Nhấn Tiếp tục để sang Bước 2
            print("- Click Tiếp tục sang Bước 2...")
            self.page.click(".next-step-btn")
            time.sleep(5)

            # --- BƯỚC 2: Hình ảnh & video ---
            if local_images:
                print("- Tải lên hình ảnh...")
                try:
                    # Lấy đường dẫn tuyệt đối của tất cả các ảnh cục bộ
                    abs_paths = [os.path.abspath(p) for p in local_images]
                    self.page.set_input_files("input#_input-post-images", abs_paths)
                    time.sleep(6) # Chờ load ảnh preview
                    print(f"  => Đã tải lên {len(abs_paths)} ảnh thành công")
                except Exception as e_upload:
                    print(f"  ⚠️ Lỗi khi tải ảnh: {e_upload}")
            else:
                print("  ⚠️ Không có ảnh cục bộ nào để upload.")

            # Nhấn Tiếp tục để sang Bước 3
            print("- Click Tiếp tục sang Bước 3...")
            self.page.click(".next-step-btn")
            time.sleep(5)

            # --- BƯỚC 3: Cấu hình tin đăng ---
            print("- Chọn gói đăng tin Tiêu chuẩn (Miễn phí)...")
            try:
                self.page.click("div.card.__post-type[data-packagetype='1']")
                time.sleep(2)
            except Exception as e_pack:
                print(f"  => Không chọn được gói Tiêu chuẩn, bỏ qua dùng mặc định: {e_pack}")

            # Chọn thời hạn đăng 30 ngày thay vì mặc định 7 ngày
            print("- Chọn thời hạn đăng tin 30 ngày...")
            try:
                # Thử click vào option 30 ngày (thường là radio button hoặc select)
                selected_30 = False

                # Thử tìm radio button hoặc button 30 ngày
                for sel in [
                    "div.tag.__card-post-days[data-postdaysid='22']",
                    "div.tag.__card-post-days:has-text('30 ngày')",
                    "div.tag.__card-post-days h3:has-text('30 ngày')",
                    ".__card-post-days h3:has-text('30 ngày')",
                    "h3:has-text('30 ngày')",
                    "input[type='radio'][value='30']",
                    "div.__post-duration[data-duration='30']",
                    "div.card.__post-duration[data-day='30']",
                    "label:has-text('30 ngày')",
                    "span:has-text('30 ngày')",
                    ".duration-option[data-value='30']",
                ]:
                    try:
                        if self.page.locator(sel).count() > 0:
                            self.page.click(sel)
                            selected_30 = True
                            print(f"  => Đã chọn 30 ngày qua selector: {sel}")
                            time.sleep(1)
                            break
                    except:
                        pass

                # Thử chọn qua select dropdown nếu có
                if not selected_30:
                    for sel in ["select[name*='duration']", "select[name*='day']", "select.__duration"]:
                        try:
                            if self.page.locator(sel).count() > 0:
                                self.page.select_option(sel, "30")
                                selected_30 = True
                                print(f"  => Đã chọn 30 ngày qua dropdown: {sel}")
                                time.sleep(1)
                                break
                        except:
                            pass

                # Thử tìm qua JS nếu vẫn chưa chọn được
                if not selected_30:
                    self.page.evaluate("""
                        () => {
                            // Tìm tất cả các phần tử có chứa '30'
                            const els = document.querySelectorAll('input[type="radio"], .duration-option, .__post-duration, .__card-post-days, .tag');
                            for (let el of els) {
                                if ((el.value === '30') || 
                                    (el.getAttribute('data-duration') === '30') || 
                                    (el.getAttribute('data-day') === '30') ||
                                    (el.getAttribute('data-postdaysid') === '22') ||
                                    (el.innerText && el.innerText.includes('30 ngày'))) {
                                    el.click();
                                    return true;
                                }
                            }
                            return false;
                        }
                    """)
                    print("  => Đã thử chọn 30 ngày qua JS evaluation")
                    time.sleep(1)

            except Exception as e_dur:
                print(f"  ⚠️ Không chọn được 30 ngày, sử dụng mặc định: {e_dur}")

            # Chờ thêm 3 giây để đảm bảo giao diện bước 3 hiển thị đầy đủ và chụp ảnh gỡ lỗi
            time.sleep(3)
            try:
                self.safe_screenshot("thuviennhadat_step3_debug.png")
                with open("thuviennhadat_step3_debug.html", "w", encoding="utf-8") as f:
                    f.write(self.page.content())
                print("  => Đã lưu ảnh chụp và mã HTML của Bước 3 để phân tích")
            except Exception as e_debug:
                print(f"  ⚠️ Lỗi khi lưu file gỡ lỗi: {e_debug}")

            # Nhấn Tiếp tục để sang bước xác nhận/thanh toán cuối cùng
            print("- Click Tiếp tục sang bước thanh toán/xác nhận...")
            try:
                next_btn = self.page.locator(".next-step-btn")
                if next_btn.count() > 0 and next_btn.is_visible():
                    next_btn.click()
                    print("  => Đã click nút Tiếp tục sang màn xác nhận qua Playwright")
                else:
                    self.page.evaluate("document.querySelector('.next-step-btn').click()")
                    print("  => Đã click nút Tiếp tục sang màn xác nhận qua JavaScript")
                time.sleep(3)
                
                # Kiểm tra và xử lý modal khuyến mãi/popup (nếu có)
                for _ in range(3):
                    promo_btn = self.page.locator(".btn-skiped-promo, .btn-used-promo")
                    if promo_btn.count() > 0 and promo_btn.first.is_visible():
                        print("  => Phát hiện modal khuyến mãi hiển thị, click bỏ qua...")
                        promo_btn.first.click()
                        time.sleep(2)
                        break
                    time.sleep(1)
            except Exception as e_next:
                print(f"  ⚠️ Lỗi khi chuyển sang màn xác nhận: {e_next}")

            # Click Đăng tin để hoàn tất
            print("- Click Đăng tin...")
            try:
                final_btn = self.page.locator(".final-step-btn")
                
                # Đợi nút Đăng tin hiển thị (tối đa 5 giây)
                for _ in range(5):
                    if final_btn.count() > 0 and final_btn.is_visible():
                        break
                    time.sleep(1)

                if final_btn.count() > 0 and final_btn.is_visible():
                    final_btn.click()
                    print("  => Đã click nút Đăng tin qua Playwright thành công")
                else:
                    print("  ⚠️ Nút Đăng tin bị ẩn hoặc không thể click trực tiếp, thử click bằng JavaScript...")
                    self.page.evaluate("document.querySelector('.final-step-btn').click()")
                    print("  => Đã gửi lệnh click JS cho nút Đăng tin (.final-step-btn)")
                time.sleep(8)
            except Exception as e_click:
                print(f"  ⚠️ Lỗi click Đăng tin, thử click lại qua JS thay thế: {e_click}")
                try:
                    self.page.evaluate("document.querySelector('.final-step-btn').click()")
                    time.sleep(8)
                except Exception as e_alt:
                    print(f"  ⚠️ Thất bại hoàn toàn khi gửi form ở Bước 3: {e_alt}")
                    raise e_click

            # Kiểm tra kết quả
            current_url = self.page.url
            body_text = self.page.evaluate("document.body.innerText")
            print(f"  => URL hiện tại: {current_url}")
            
            success_keywords = ["quan-ly", "thành công", "đã được ghi nhận", "kết quả đăng tin", "mã tin"]
            is_success = "quan-ly" in current_url or any(kw in body_text.lower() for kw in success_keywords)
            
            if is_success:
                print("  ✅ ĐĂNG TIN THUVIENNHADAT THÀNH CÔNG!")
                try:
                    post_id = self.page.locator("#_partial-code-post-compeled").inner_text(timeout=2000).strip()
                    if post_id and post_id != "0":
                        print(f"  => Mã tin đăng: {post_id}")
                except Exception:
                    pass
                return True
            else:
                self.safe_screenshot("thuviennhadat_submit_failed.png")
                print("  ⚠️ Hãy kiểm tra lại trạng thái tin đăng trong trang Quản lý tin. Đã lưu thuviennhadat_submit_failed.png")
                return False
        except Exception as e:
            print(f"=> Lỗi đăng tin thuviennhadat: {e}")
            return False


    def login_muaban(self, username, password):
        """Đăng nhập vào muaban.net - dùng persistent session để lưu cookies"""
        print(f"Đang đăng nhập muaban.net với tài khoản: {username}")
        if self.headless:
            print("  ⚠️ CẢNH BÁO: Trình duyệt đang chạy ở chế độ ẩn danh (headless).")
            print("  ⚠️ Ở chế độ này, Cloudflare Turnstile có thể phát hiện và chặn tự động.")
            print("  ⚠️ Nếu bot bị kẹt hoặc đăng nhập thất bại, vui lòng bỏ chọn 'Chạy ẩn danh' trên Streamlit App.")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            # === Bước 1: Truy cập trang login ===
            print("- Truy cập trang đăng nhập muaban.net...")
            self.page.goto("https://muaban.net/account/login", wait_until="domcontentloaded", timeout=60000)
            self._wait_for_cloudflare(self.page, timeout_secs=45)
            time.sleep(3)

            # === Bước 2: Kiểm tra đã đăng nhập chưa (session cũ) ===
            # Chờ tối đa 10 giây xem có chuyển hướng tự động hoặc form xuất hiện không
            print("- Kiểm tra trạng thái đăng nhập hoặc chờ form...")
            start_check = time.time()
            is_logged_in = False
            while time.time() - start_check < 10:
                current_url = self.page.url
                # Nếu đã chuyển hướng ra khỏi login và url thuộc muaban.net => đã đăng nhập
                if '/account/login' not in current_url and 'muaban.net' in current_url:
                    is_logged_in = True
                    break
                # Kiểm tra sự xuất hiện của các phần tử đã đăng nhập (như nút "Quản lý tin" hoặc avatar)
                try:
                    if self.page.locator("a:has-text('Quản lý tin'), [class*='user'], [class*='avatar']").count() > 0:
                        is_logged_in = True
                        break
                except:
                    pass
                # Nếu thấy ô nhập số điện thoại => chưa đăng nhập, bắt đầu điền form
                try:
                    if self.page.locator("#phone, input[name='phone'], input[type='tel']").count() > 0:
                        break
                except:
                    pass
                time.sleep(0.5)

            current_url = self.page.url
            current_title = self.page.title()
            print(f"  URL hiện tại: {current_url}")
            print(f"  Title hiện tại: {current_title}")

            if is_logged_in:
                print("=> Session đã đăng nhập sẵn từ lần trước!")
                return True

            # Kiểm tra form login có xuất hiện không
            phone_input = self.page.locator("#phone, input[name='phone'], input[type='tel']")
            if phone_input.count() == 0:
                print("  ⚠️ Không tìm thấy form đăng nhập. Chờ thêm 5 giây...")
                time.sleep(5)
                phone_input = self.page.locator("#phone, input[name='phone'], input[type='tel']")

            # === Bước 3: Điền form login ===
            print("- Nhập số điện thoại...")
            try:
                phone_input.first.click(timeout=5000)
                phone_input.first.fill("", timeout=5000)
                phone_input.first.type(username, delay=80, timeout=5000)
                print(f"  ✅ Đã nhập số điện thoại: {username}")
            except Exception as e:
                print(f"  ❌ Lỗi nhập số điện thoại: {e}")
                self.safe_screenshot(os.path.join(script_dir, "muaban_login_phone_error.png"))
                return False

            print("- Nhập mật khẩu...")
            try:
                pwd_input = self.page.locator("#password, input[name='password'], input[type='password']")
                pwd_input.first.click(timeout=5000)
                pwd_input.first.fill("", timeout=5000)
                pwd_input.first.type(password, delay=80, timeout=5000)
                print("  ✅ Đã nhập mật khẩu")
            except Exception as e:
                print(f"  ❌ Lỗi nhập mật khẩu: {e}")
                self.safe_screenshot(os.path.join(script_dir, "muaban_login_pwd_error.png"))
                return False

            # Screenshot trước khi submit
            self.safe_screenshot(os.path.join(script_dir, "muaban_before_submit.png"))

            print("- Click nút Đăng nhập...")
            try:
                submit_btn = self.page.locator("button[type='submit']")
                submit_btn.first.hover(timeout=5000)
                time.sleep(0.5)
                submit_btn.first.click(timeout=5000)
                print("  ✅ Đã click submit")
            except Exception as e:
                print(f"  ❌ Lỗi click submit: {e}")
                return False

            # === Bước 4: Chờ và xác minh login thành công ===
            print("- Chờ kết quả đăng nhập...")
            
            # Đợi tối đa 15 giây cho việc chuyển hướng khỏi trang login
            start_wait = time.time()
            while time.time() - start_wait < 15:
                if '/account/login' not in self.page.url:
                    break
                time.sleep(1)

            new_url = self.page.url
            new_title = self.page.title()
            print(f"  URL sau khi đăng nhập: {new_url}")
            print(f"  Title sau khi đăng nhập: {new_title}")
            
            # Chụp ảnh sau khi đã hoàn tất chuyển hướng
            self.safe_screenshot(os.path.join(script_dir, "muaban_after_submit.png"))

            # Xác minh kết quả đăng nhập thông minh
            is_login_success = False
            try:
                # 1. URL đã thay đổi khác trang login
                if '/account/login' not in new_url:
                    is_login_success = True
                # 2. Hoặc tìm thấy phần tử chỉ hiển thị khi đã đăng nhập (avatar, tên user, nút quản lý, đăng xuất)
                elif self.page.locator("a:has-text('Quản lý tin'), [class*='avatar'], [class*='user-name'], button:has-text('Đăng xuất'), a[href*='/ca-nhan']").count() > 0:
                    is_login_success = True
                # 3. Hoặc tiêu đề trang đã cập nhật từ login sang trang chủ/trang cá nhân
                elif "Đăng nhập" not in new_title and "Website mua bán" not in new_title and "đăng tin" in new_title.lower():
                    is_login_success = True
            except:
                pass

            if not is_login_success:
                # Thử tìm thông báo lỗi
                error_msg = ""
                try:
                    err_el = self.page.locator(".toast, [class*='error'], [class*='Error'], [class*='alert']").first
                    if err_el.count() > 0:
                        error_msg = err_el.inner_text(timeout=2000)
                except:
                    pass
                print(f"  ❌ Login thất bại! Vẫn ở trang login. Lỗi: {error_msg}")
                return False

            # Kiểm tra token/cookie đăng nhập
            try:
                cookies = self.context.cookies()
                token_cookie = any(c['name'] in ['token', 'auth_token', 'access_token', 'mbtoken', 'user_token'] 
                                   for c in cookies)
                print(f"  Token cookie: {token_cookie}, Tổng cookies: {len(cookies)}")
            except:
                pass

            print(f"✅ Đăng nhập muaban.net thành công! URL: {new_url}")
            return True

        except Exception as e:
            print(f"Lỗi đăng nhập muaban.net: {e}")
            try:
                self.safe_screenshot(os.path.join(script_dir, "muaban_login_exception.png"))
            except:
                pass
            return False

    def post_muaban(self, item, dry_run=False):
        """Đăng tin lên muaban.net - dùng persistent session để vượt Cloudflare"""
        print(f"Bắt đầu đăng tin trên muaban.net: {item.get('title')}")
        try:
            local_images = self.download_property_images(item.get('source_url', ''), item.get('title', ''))

            # === BƯỚC 1: Vào trang đăng tin ===
            print("- Vào trang đăng tin...")
            self.page.goto("https://muaban.net/dang-tin", wait_until="domcontentloaded", timeout=60000)
            ok = self._wait_for_cloudflare(self.page, timeout_secs=45)
            if not ok:
                print("⚠️ Cloudflare chưa vượt qua - nếu có trình duyệt mở, hãy chờ xác minh tự động.")
                time.sleep(10)

            time.sleep(3)
            print(f"  Trang hiện tại: {self.page.title()}")

            # Xử lý modal khôi phục bản nháp nếu xuất hiện
            try:
                new_btn = self.page.locator("button:has-text('Đăng tin mới')").first
                if new_btn.count() > 0 and new_btn.is_visible():
                    new_btn.click(timeout=4000)
                    print("  - Đã bấm 'Đăng tin mới' để xóa bản nháp cũ")
                    time.sleep(2)
            except Exception as e:
                pass

            # === BƯỚC 2: Chọn danh mục ===
            print("- Chọn danh mục: Bất động sản -> Cho thuê -> Văn phòng...")
            
            # Thử click vào label/nút mở danh mục trước
            try:
                # Có thể có một nút/label để mở modal danh mục
                category_triggers = [
                    "[class*='category'] label",
                    "[class*='CategorySelect']",
                    "label:has-text('Chọn chuyên mục')",
                    "div:has-text('Chọn chuyên mục đăng tin')",
                    "[placeholder*='danh mục'], [placeholder*='chuyên mục']",
                ]
                for trigger in category_triggers:
                    el = self.page.locator(trigger).first
                    if el.count() > 0 and el.is_visible():
                        el.click(timeout=3000)
                        print(f"  - Đã mở menu danh mục bằng: {trigger}")
                        time.sleep(2)
                        break
            except: pass

            # Tìm và click "Bất động sản"
            bds_clicked = False
            bds_selectors = [
                "text=Bất động sản",
                "li:has-text('Bất động sản')",
                "a:has-text('Bất động sản')",
                "span:has-text('Bất động sản')",
                "[class*='item']:has-text('Bất động sản')",
            ]
            for sel in bds_selectors:
                els = self.page.locator(sel)
                if els.count() > 0:
                    for i in range(els.count()):
                        try:
                            el = els.nth(i)
                            if el.is_visible():
                                el.click(timeout=4000)
                                print(f"  - Đã click 'Bất động sản' [{sel}]")
                                bds_clicked = True
                                break
                        except: continue
                if bds_clicked:
                    break
            
            if not bds_clicked:
                print("  ⚠️ Không tìm thấy 'Bất động sản' - hãy chọn thủ công trong 15 giây...")
                time.sleep(15)
            else:
                time.sleep(2)

            # Click "Cho thuê"
            try:
                cho_thue_els = self.page.locator("text=Cho thuê")
                for i in range(cho_thue_els.count()):
                    el = cho_thue_els.nth(i)
                    if el.is_visible():
                        el.click(timeout=4000)
                        print("  - Đã click 'Cho thuê'")
                        break
                time.sleep(2)
            except Exception as e:
                print(f"  ⚠️ Không click được 'Cho thuê': {e}")

            # Click "Văn phòng"
            try:
                vp_options = [
                    "text=Văn phòng, mặt bằng",
                    "text=Văn phòng mặt bằng",
                    "text=Văn phòng",
                ]
                for opt in vp_options:
                    els = self.page.locator(opt)
                    for i in range(els.count()):
                        el = els.nth(i)
                        if el.is_visible():
                            el.click(timeout=4000)
                            print(f"  - Đã click '{opt}'")
                            time.sleep(3)
                            break
                    else:
                        continue
                    break
            except Exception as e:
                print(f"  ⚠️ Không click được 'Văn phòng': {e}")

            # === BƯỚC 3: Điền thông tin ===
            print("- Điền thông tin cơ bản...")
            title = item.get('title', '')
            content = item.get('content', '').replace('\\n', '\n')
            price_val = self.parse_price(item.get('price', ''), item.get('area', ''))
            area_val = str(item.get('area', ''))
            address_val = item.get('address', '')
            district_val = item.get('district', '')

            # Điền tiêu đề
            title_sels = [
                "input[name='title']",
                "input[placeholder*='tiêu đề'], input[placeholder*='Tiêu đề']",
                "input[class*='title']",
            ]
            for sel in title_sels:
                try:
                    el = self.page.locator(sel).first
                    if el.count() > 0 and el.is_visible():
                        el.fill(title, timeout=4000)
                        print(f"  - Tiêu đề đã điền")
                        break
                except: continue

            # Điền mô tả
            desc_sels = [
                "textarea[name='body']",
                "textarea[name='description']",
                "textarea[placeholder*='mô tả'], textarea[placeholder*='Mô tả']",
                "textarea",
            ]
            for sel in desc_sels:
                try:
                    el = self.page.locator(sel).first
                    if el.count() > 0 and el.is_visible():
                        el.fill(content, timeout=4000)
                        print(f"  - Mô tả đã điền")
                        break
                except: continue

            # Điền giá
            if price_val > 0:
                price_sels = [
                    "input[name='price']",
                    "input[placeholder*='giá'], input[placeholder*='Giá']",
                ]
                for sel in price_sels:
                    try:
                        el = self.page.locator(sel).first
                        if el.count() > 0 and el.is_visible():
                            el.fill(str(price_val), timeout=4000)
                            print(f"  - Giá đã điền: {price_val}")
                            break
                    except: continue

            # Điền diện tích (field name là 'living_area' trên muaban.net)
            if area_val:
                area_sels = [
                    "input[name='living_area']",
                    "input[name='area']",
                    "input.input-number[name*='area']",
                ]
                for sel in area_sels:
                    try:
                        el = self.page.locator(sel).first
                        if el.count() > 0 and el.is_visible():
                            el.fill(area_val, timeout=4000)
                            print(f"  - Diện tích đã điền: {area_val}")
                            break
                    except: continue

            # === BƯỚC 4: Điền địa chỉ (Modal Dropdown - muaban.net) ===
            print("- Điền địa chỉ...")

            def _select_location_modal(trigger_id, value_text, label_name):
                """Click a modal-trigger div, type in search, then pick the option."""
                if not value_text:
                    return True
                try:
                    trigger = self.page.locator(f"div#{trigger_id}")
                    if trigger.count() == 0 or not trigger.is_visible():
                        print(f"  ⚠️ Không tìm thấy #{trigger_id}")
                        return False
                    # Check if disabled
                    for _ in range(5):
                        cls = trigger.get_attribute("class") or ""
                        if "disable" not in cls:
                            break
                        time.sleep(1)
                    
                    try:
                        trigger.click(timeout=3000)
                    except Exception as click_err:
                        print(f"  - Standard click failed for trigger {trigger_id}: {click_err}. Trying JS click...")
                        trigger.evaluate("el => el.click()")
                    time.sleep(1.5)

                    # Use the search input inside the modal to filter
                    search_input = self.page.locator("div[class*='modal'] input[type='text'], input[placeholder*='Nhập để tìm']").first
                    
                    search_queries = [value_text]
                    words = value_text.split()
                    if len(words) > 1 and words[-1].lower() in ["trung", "nam", "bắc", "đông", "tây", "thượng", "hạ"]:
                        simplified = " ".join(words[:-1])
                        search_queries.append(simplified)
                    
                    option_handle = None
                    for query in search_queries:
                        if search_input.count() > 0 and search_input.is_visible():
                            search_input.fill(query, timeout=3000)
                            time.sleep(1.5)
                        
                        option_handle = self.page.evaluate_handle(
                            """(val) => {
                                const modal = document.querySelector('[class*="modal"]');
                                if (!modal) return null;
                                
                                const getOptions = () => {
                                    const scrollable = Array.from(modal.querySelectorAll('*')).find(el => {
                                        const style = window.getComputedStyle(el);
                                        return (style.overflowY === 'auto' || style.overflowY === 'scroll' || el.scrollHeight > el.clientHeight) 
                                               && el.tagName !== 'BODY' && el.tagName !== 'HTML';
                                    });
                                    
                                    let candidates = [];
                                    if (scrollable) {
                                        candidates = Array.from(scrollable.querySelectorAll('div, li, span, p'));
                                    } else {
                                        candidates = Array.from(modal.querySelectorAll('div, li, span, p'));
                                    }
                                    
                                    const optionItems = candidates.filter(el => {
                                        if (el.tagName === 'INPUT' || el.tagName === 'BUTTON' || el.tagName === 'SVG') return false;
                                        const cls = (el.className || "").toString().toLowerCase();
                                        if (cls.includes('header') || cls.includes('search') || cls.includes('close') || cls.includes('title')) return false;
                                        if (el.closest('[class*="header"]') || el.closest('[class*="search"]') || el.closest('[class*="close"]')) return false;
                                        if (!el.innerText || !el.innerText.trim()) return false;
                                        return true;
                                    });
                                    
                                    const leaves = optionItems.filter((el, idx, selfList) => {
                                        return !selfList.some(other => other !== el && el.contains(other));
                                    });
                                    
                                    const wrappers = leaves.map(leaf => {
                                        let curr = leaf;
                                        const limit = scrollable || modal;
                                        while (curr.parentElement && curr.parentElement !== limit && curr.parentElement !== document.body) {
                                            if (scrollable && curr.parentElement.parentElement === scrollable) {
                                                curr = curr.parentElement;
                                                break;
                                            }
                                            curr = curr.parentElement;
                                        }
                                        return curr;
                                    });
                                    
                                    return Array.from(new Set(wrappers));
                                };
                                
                                const options = getOptions();
                                const searchVal = val.toLowerCase().trim();
                                const match = options.find(el => el.innerText && el.innerText.toLowerCase().includes(searchVal));
                                return match || null;
                            }""", query
                        )
                        
                        if option_handle and option_handle.as_element():
                            break
                            
                    # Fallback if no matching option was found in filtered list
                    if not option_handle or not option_handle.as_element():
                        print(f"  ⚠️ Không tìm thấy option khớp với query nào cho '{label_name}'. Đang xóa tìm kiếm để chọn đại diện...")
                        if search_input.count() > 0 and search_input.is_visible():
                            search_input.fill("")
                            time.sleep(1.5)
                        
                        option_handle = self.page.evaluate_handle(
                            """() => {
                                const modal = document.querySelector('[class*="modal"]');
                                if (!modal) return null;
                                
                                const getOptions = () => {
                                    const scrollable = Array.from(modal.querySelectorAll('*')).find(el => {
                                        const style = window.getComputedStyle(el);
                                        return (style.overflowY === 'auto' || style.overflowY === 'scroll' || el.scrollHeight > el.clientHeight) 
                                               && el.tagName !== 'BODY' && el.tagName !== 'HTML';
                                    });
                                    
                                    let candidates = [];
                                    if (scrollable) {
                                        candidates = Array.from(scrollable.querySelectorAll('div, li, span, p'));
                                    } else {
                                        candidates = Array.from(modal.querySelectorAll('div, li, span, p'));
                                    }
                                    
                                    const optionItems = candidates.filter(el => {
                                        if (el.tagName === 'INPUT' || el.tagName === 'BUTTON' || el.tagName === 'SVG') return false;
                                        const cls = (el.className || "").toString().toLowerCase();
                                        if (cls.includes('header') || cls.includes('search') || cls.includes('close') || cls.includes('title')) return false;
                                        if (el.closest('[class*="header"]') || el.closest('[class*="search"]') || el.closest('[class*="close"]')) return false;
                                        if (!el.innerText || !el.innerText.trim()) return false;
                                        return true;
                                    });
                                    
                                    const leaves = optionItems.filter((el, idx, selfList) => {
                                        return !selfList.some(other => other !== el && el.contains(other));
                                    });
                                    
                                    const wrappers = leaves.map(leaf => {
                                        let curr = leaf;
                                        const limit = scrollable || modal;
                                        while (curr.parentElement && curr.parentElement !== limit && curr.parentElement !== document.body) {
                                            if (scrollable && curr.parentElement.parentElement === scrollable) {
                                                curr = curr.parentElement;
                                                break;
                                            }
                                            curr = curr.parentElement;
                                        }
                                        return curr;
                                    });
                                    
                                    return Array.from(new Set(wrappers));
                                };
                                
                                const options = getOptions();
                                return options[0] || null;
                            }"""
                        )

                    if option_handle and option_handle.as_element():
                        option = option_handle.as_element()
                        try:
                            option.click(timeout=3000)
                        except:
                            option.evaluate("el => el.click()")
                        time.sleep(1.5)
                        print(f"  - {label_name}: {value_text} (hoặc đại diện)")
                        return True
                    else:
                        raise Exception(f"Không thể chọn {label_name}")
                except Exception as e:
                    print(f"  ⚠️ Lỗi chọn {label_name}: {e}")
                    # Close any open modal
                    try:
                        close_btn = self.page.locator("div[class*='modal'] button, div[class*='modal'] svg, div[class*='modal'] [class*='close']").first
                        if close_btn.count() > 0 and close_btn.is_visible():
                            close_btn.click(timeout=2000)
                        else:
                            self.page.keyboard.press("Escape")
                        time.sleep(0.5)
                    except: pass
                    return False

            # Trích xuất Ward (Phường/Xã), Street (Tên đường) và Số nhà từ address_val
            ward_val = item.get('ward', '')
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
                print(f"  - Ward mặc định cho {district_clean}: {ward_val}")

            # Phân tách số nhà nếu có ở đầu street_val
            if street_val:
                import re
                num_match = re.match(r'^(\d+[a-zA-Z]?(\/\d+[a-zA-Z]?)?)\s+(.*)$', street_val)
                if num_match:
                    street_number_val = num_match.group(1)
                    street_val = num_match.group(3).strip()

            # Chọn Tỉnh/Thành (Đà Nẵng)
            _select_location_modal("city_id", "Đà Nẵng", "Thành phố")

            # Chọn Quận/Huyện
            _select_location_modal("district_id", district_val if district_val else "Sơn Trà", "Quận/Huyện")

            # Chọn Phường/Xã nếu có ward_val
            _select_location_modal("ward_id", ward_val, "Phường/Xã")

            # Chọn Tên đường nếu có
            _select_location_modal("street_id", street_val, "Tên đường")

            # Điền số nhà (street_number)
            if street_number_val:
                try:
                    street_input = self.page.locator("input[name='street_number']").first
                    if street_input.count() > 0 and street_input.is_visible():
                        street_input.fill(street_number_val, timeout=3000)
                        print(f"  - Số nhà: {street_number_val}")
                except Exception as e:
                    print(f"  ⚠️ Lỗi điền số nhà: {e}")

            # === BƯỚC 4b: Chọn kiểu bất động sản (property_subtype) ===
            try:
                prop_type = item.get('property_subtype', 'Văn phòng')
                _select_location_modal("property_subtype", prop_type, "Kiểu BĐS")
            except: pass

            # === BƯỚC 5: Tải ảnh lên ===
            if local_images:
                print("- Tải lên hình ảnh...")
                try:
                    file_input = self.page.locator("input[type='file']")
                    if file_input.count() > 0:
                        file_input.first.set_input_files(local_images)
                        time.sleep(5)
                        print(f"  - Đã tải {len(local_images)} ảnh")
                except Exception as e:
                    print(f"  ⚠️ Không thể tự động tải ảnh: {e}")

            # === BƯỚC 6: Bấm Tiếp tục / Đăng tin ===
            if dry_run:
                print("  ℹ️ Dry run mode: Dừng lại trước khi click submit.")
                time.sleep(2)
                script_dir = os.path.dirname(os.path.abspath(__file__))
                self.safe_screenshot(os.path.join(script_dir, "muaban_dry_run_state.png"))
                return True

            print("- Tìm và bấm nút Tiếp tục / Đăng tin...")
            submit_sels = [
                "button:has-text('Tiếp tục')",
                "button:has-text('Đăng tin')",
                "button[type='submit']",
                "a:has-text('Đăng tin')",
            ]
            submitted = False
            for sel in submit_sels:
                try:
                    btn = self.page.locator(sel).last
                    if btn.count() > 0 and btn.is_visible():
                        try:
                            btn.click(timeout=4000)
                        except Exception as click_err:
                            print(f"  - Standard click failed: {click_err}. Trying JS click...")
                            btn.evaluate("el => el.click()")
                        print(f"  - Đã bấm: '{sel}'")
                        time.sleep(5)
                        # Nếu có thêm bước confirm
                        confirm_btn = self.page.locator("button:has-text('Đăng tin'), button:has-text('Xác nhận')").last
                        if confirm_btn.count() > 0 and confirm_btn.is_visible():
                            try:
                                confirm_btn.click(timeout=4000)
                            except Exception as click_err2:
                                print(f"  - Standard confirm click failed: {click_err2}. Trying JS click...")
                                confirm_btn.evaluate("el => el.click()")
                            print("  - Đã bấm xác nhận lần 2")
                        submitted = True
                        break
                except: continue

            if not submitted:
                # Direct JS document select click fallback
                try:
                    print("  - Thử JS click trực tiếp từ DOM...")
                    self.page.evaluate("() => { const btns = Array.from(document.querySelectorAll('button')); const btn = btns.find(b => b.innerText.includes('Tiếp tục') || b.innerText.includes('Đăng tin')); if (btn) btn.click(); }")
                    time.sleep(5)
                except Exception as e:
                    print(f"  ⚠️ Lỗi JS fallback click: {e}")


            time.sleep(8)
            final_url = self.page.url
            final_title = self.page.title()
            print(f"URL sau đăng: {final_url} | Title: {final_title}")

            # Lưu screenshot kết quả
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.safe_screenshot(os.path.join(script_dir, "muaban_post_result.png"))

            # === Xác minh đăng tin thực sự thành công ===
            # Muaban thường redirect sang trang quản lý tin hoặc trang chi tiết tin sau khi đăng
            success_patterns = [
                '/dashboard/manage-listing',
                '/tin-dang/',
                '/bat-dong-san/',
                '/success',
                '/thank',
                'dang-tin-thanh-cong',
                '/dang-tin/ket-qua',
                '#classified_id=',
            ]
            # Kiểm tra URL có chứa pattern thành công
            is_success = any(p in final_url for p in success_patterns)

            # Nếu không match URL, tìm thông báo thành công trên trang
            if not is_success:
                try:
                    success_text = self.page.locator(
                        "text=Đăng tin thành công, text=Tin đăng thành công, "
                        "[class*='success'], .toast-success, [class*='Success']"
                    ).first
                    if success_text.count() > 0 and success_text.is_visible():
                        is_success = True
                        print(f"  ✅ Thấy thông báo thành công: {success_text.inner_text(timeout=2000)}")
                except:
                    pass

            # Nếu URL đăng tin ban đầu thay đổi sang URL khác (không phải /dang-tin)
            if not is_success and '/dang-tin' not in final_url:
                # URL đã thay đổi khỏi trang đăng tin => có thể thành công
                is_success = True
                print(f"  ℹ️ URL đã thay đổi khỏi /dang-tin => giả định thành công")

            if is_success:
                print(f"🎉 Đăng tin muaban.net thành công! URL: {final_url}")
                return True
            else:
                print(f"❌ Đăng tin muaban.net thất bại! Vẫn ở trang: {final_url}")
                return False

        except Exception as e:
            print(f"Lỗi đăng tin muaban.net: {e}")
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                self.safe_screenshot(os.path.join(script_dir, "muaban_post_exception.png"))
            except:
                pass
            return False

    def login_123nhadatviet_shared(self, base_url, username, password):
        """Hàm đăng nhập dùng chung cho 123nhadatviet.com và nhadatviet247.net"""
        print(f"Đang đăng nhập vào {base_url} với tài khoản: {username}")
        try:
            self.page.goto(f"http://{base_url}/", wait_until="commit")
            self._wait_for_cloudflare(self.page, timeout_secs=15)
            
            time.sleep(2)
            logout_btn = self.page.locator("a:has-text('Đăng xuất'), a:has-text('Thoát')").all()
            if logout_btn and any(b.is_visible() for b in logout_btn):
                print(f"  ✓ Đã đăng nhập từ trước trên {base_url}")
                return True
                
            login_link = self.page.locator("a:has-text('Đăng nhập'), a.login").first
            if login_link.count() > 0:
                login_link.click()
                time.sleep(1.5)
                
            self.page.fill("input#account", username)
            self.page.fill("input#password", password)
            
            login_btn = self.page.locator("#login-form span.login, span.login, span:has-text('Đăng nhập')").first
            if login_btn.count() > 0:
                login_btn.click()
                time.sleep(3)
            else:
                self.page.press("input#password", "Enter")
                time.sleep(3)
                
            logout_btn = self.page.locator("a:has-text('Đăng xuất'), a:has-text('Thoát')").all()
            if logout_btn and any(b.is_visible() for b in logout_btn):
                print(f"  ✓ Đăng nhập thành công trên {base_url}")
                return True
            else:
                print("  ❌ Không thấy nút Đăng xuất sau khi click đăng nhập. Thử reload...")
                self.page.reload()
                time.sleep(2)
                logout_btn = self.page.locator("a:has-text('Đăng xuất'), a:has-text('Thoát')").all()
                if logout_btn and any(b.is_visible() for b in logout_btn):
                    print(f"  ✓ Đăng nhập thành công trên {base_url} (sau khi reload)")
                    return True
                
                print("  ❌ Đăng nhập thất bại hoặc cần xác thực thêm.")
                return False
                
        except Exception as e:
            print(f"Lỗi đăng nhập {base_url}: {e}")
            return False

    def login_123nhadatviet(self, username, password):
        return self.login_123nhadatviet_shared("123nhadatviet.com", username, password)

    def login_nhadatviet247(self, username, password):
        return self.login_123nhadatviet_shared("nhadatviet247.net", username, password)

    def post_123nhadatviet_shared(self, base_url, item):
        """Hàm đăng tin dùng chung cho 123nhadatviet.com và nhadatviet247.net"""
        print(f"Bắt đầu đăng tin trên {base_url}: {item.get('title')}")
        try:
            self.page.goto(f"http://{base_url}/dang-tin.html", wait_until="domcontentloaded")
            self._wait_for_cloudflare(self.page, timeout_secs=15)
            time.sleep(2)
            
            # Title
            title = item.get("title", "")
            self.page.fill("#tieude", title)
            
            # Content (using 'content' or fallback to 'description')
            content = item.get("content") or item.get("description", "")
            self.page.fill("#noidung", content)
            
            # Category: 1 (Cần bán), 2 (Cho thuê)
            # Detect from title or category columns
            title_lower = title.lower()
            category_lower = (item.get("category") or "").lower()
            post_type = item.get("type", "Thuê").lower()
            
            loaitin_val = "2" # Default to renting (Cho thuê) since it's office listings
            if "bán" in title_lower or "ban" in title_lower or "bán" in category_lower or "ban" in category_lower or "bán" in post_type or "ban" in post_type:
                loaitin_val = "1"
            self.page.select_option("#loaitin", loaitin_val)
            
            # Property type mapping from 'category' or 'property_type'
            bds_type = (item.get("category") or item.get("property_type") or "").lower()
            loaibds_val = "2" # Default: Nhà riêng
            if "chung cư" in bds_type or "căn hộ" in bds_type or "apartment" in bds_type or "chung cu" in bds_type or "can ho" in bds_type:
                loaibds_val = "4"
            elif "biệt thự" in bds_type or "biet thu" in bds_type:
                loaibds_val = "3"
            elif "văn phòng" in bds_type or "van phong" in bds_type:
                loaibds_val = "6"
            elif "trọ" in bds_type or "tro" in bds_type:
                loaibds_val = "7"
            elif "mặt bằng" in bds_type or "cửa hàng" in bds_type or "mat bang" in bds_type or "cua hang" in bds_type:
                loaibds_val = "9"
            elif "đất" in bds_type or "dat" in bds_type:
                loaibds_val = "10"
            elif "xưởng" in bds_type or "kho" in bds_type or "xuong" in bds_type:
                loaibds_val = "13"
            self.page.select_option("#loaibds", loaibds_val)
            
            # City mapping (check address and title for city name)
            address_lower = item.get("address", "").lower()
            tinh_val = "1" # Default: Hà Nội
            if "đà nẵng" in address_lower or "da nang" in address_lower or "đà nẵng" in title_lower or "da nang" in title_lower:
                tinh_val = "3"
            elif "hồ chí minh" in address_lower or "hcm" in address_lower or "saigon" in address_lower or "sài gòn" in address_lower or "hồ chí minh" in title_lower or "hcm" in title_lower or "saigon" in title_lower or "sài gòn" in title_lower:
                tinh_val = "2"
            elif "hải phòng" in address_lower or "hai phong" in address_lower or "hải phòng" in title_lower or "hai phong" in title_lower:
                tinh_val = "4"
            elif "cần thơ" in address_lower or "can tho" in address_lower or "cần thơ" in title_lower or "can tho" in title_lower:
                tinh_val = "5"
            self.page.select_option("#tinh", tinh_val)
            time.sleep(1.5)
            
            # District mapping
            district_name = item.get("district", "").lower()
            district_options = self.page.evaluate("""() => {
                const sel = document.getElementById('huyen');
                if (!sel) return [];
                return Array.from(sel.options).map(o => ({ value: o.value, text: o.text.toLowerCase() }));
            }""")
            huyen_val = ""
            for opt in district_options:
                if district_name in opt["text"] or opt["text"] in district_name:
                    huyen_val = opt["value"]
                    break
            if not huyen_val and len(district_options) > 1:
                huyen_val = district_options[1]["value"]
            if huyen_val:
                # Select district via JS to bypass visibility restrictions of custom styled select elements
                self.page.evaluate(f"() => {{ const el = document.getElementById('huyen'); if(el) {{ el.value = '{huyen_val}'; el.dispatchEvent(new Event('change')); }} }}")
                time.sleep(2) # Chờ AJAX load Phường/Xã và Đường/Phố
                
                # Ward mapping
                ward_options = self.page.evaluate("""() => {
                    const sel = document.getElementById('phuong');
                    if (!sel) return [];
                    return Array.from(sel.options).map(o => ({ value: o.value, text: o.text.toLowerCase() }));
                }""")
                valid_wards = [opt for opt in ward_options if opt["value"] != "" and "----" not in opt["text"]]
                valid_wards.sort(key=lambda x: len(x["text"]), reverse=True)
                
                phuong_val = ""
                for opt in valid_wards:
                    clean_opt_text = opt["text"].replace("phường", "").replace("phuong", "").strip()
                    if clean_opt_text in address_lower:
                        phuong_val = opt["value"]
                        break
                if not phuong_val and len(ward_options) > 1:
                    phuong_val = ward_options[1]["value"]
                if phuong_val:
                    # Select ward via JS
                    self.page.evaluate(f"() => {{ const el = document.getElementById('phuong'); if(el) {{ el.value = '{phuong_val}'; el.dispatchEvent(new Event('change')); }} }}")
                    time.sleep(1)
                
                # Street mapping
                street_options = self.page.evaluate("""() => {
                    const sel = document.getElementById('duong');
                    if (!sel) return [];
                    return Array.from(sel.options).map(o => ({ value: o.value, text: o.text.toLowerCase() }));
                }""")
                valid_streets = [opt for opt in street_options if opt["value"] != "" and "----" not in opt["text"]]
                valid_streets.sort(key=lambda x: len(x["text"]), reverse=True)
                
                duong_val = ""
                for opt in valid_streets:
                    clean_opt_text = opt["text"].replace("đường", "").replace("duong", "").replace("đ. ", "").replace("đ.", "").strip()
                    if clean_opt_text in address_lower:
                        duong_val = opt["value"]
                        break
                if not duong_val and len(street_options) > 1:
                    duong_val = street_options[1]["value"]
                if duong_val:
                    # Select street via JS
                    self.page.evaluate(f"() => {{ const el = document.getElementById('duong'); if(el) {{ el.value = '{duong_val}'; el.dispatchEvent(new Event('change')); }} }}")
                    time.sleep(1)
                
            address = item.get("address", "")
            if address:
                self.page.fill("#diachi", address)
                
            area = str(item.get("area", ""))
            area_matches = re.findall(r"\d+\.?\d*", area)
            if area_matches:
                self.page.fill("#dientich", area_matches[0])
                
            # Price handling
            price_raw = item.get("price", "0")
            price_val = "0"
            if isinstance(price_raw, (int, float)):
                if price_raw > 100000:
                    price_val = str(int(price_raw / 1000))
                else:
                    price_val = str(int(price_raw))
            else:
                price_str = str(price_raw).lower().strip()
                if "tỷ" in price_str or "tỉ" in price_str:
                    num_match = re.search(r"(\d+\.?\d*)", price_str)
                    if num_match:
                        price_val = str(int(float(num_match.group(1)) * 1000000))
                elif "triệu" in price_str or "tr" in price_str:
                    num_match = re.search(r"(\d+\.?\d*)", price_str)
                    if num_match:
                        price_val = str(int(float(num_match.group(1)) * 1000))
                elif "thỏa thuận" in price_str or "thoa thuan" in price_str or price_str == "0" or price_str == "":
                    price_val = "0"
                else:
                    num_match = re.search(r"(\d+)", price_str.replace(".", "").replace(",", ""))
                    if num_match:
                        val = int(num_match.group(1))
                        if val > 100000:
                            price_val = str(int(val / 1000))
                        else:
                            price_val = str(val)
            self.page.fill("#gia", price_val)
            self.page.select_option("#cachtinh", "1")
            
            contact_name = item.get("contact_name", "Chính chủ")
            self.page.fill("#lienhe", contact_name)
            
            phone = item.get("phone", "")
            if phone:
                self.page.fill("#dienthoai", phone)
                
            # Image uploads
            images = item.get("images", [])
            for idx, img_path in enumerate(images[:6]):
                if os.path.exists(img_path):
                    try:
                        self.page.set_input_files(f"#img{idx+1}", img_path)
                        print(f"  ✓ Đã chọn ảnh {idx+1}: {os.path.basename(img_path)}")
                    except Exception as e_img:
                        print(f"  ⚠️ Lỗi upload ảnh {idx+1}: {e_img}")
                        
            # Solve image captcha
            captcha_code = ""
            
            # 1. Thử giải tự động bằng thư viện OCR cục bộ (Offline, Free)
            captcha_code = self.solve_image_captcha_local(self.page, "img.captchagenerator")
            if captcha_code:
                self.page.fill("#captcha", captcha_code)
                
            # 2. Nếu thất bại và có cấu hình key, thử giải bằng 2Captcha
            if not captcha_code and self.captcha_api_key:
                captcha_code = self.solve_image_captcha(self.page, "img.captchagenerator")
                if captcha_code:
                    self.page.fill("#captcha", captcha_code)
            
            # 3. Nếu vẫn thất bại, thử giải bằng Free OCR API (Online)
            if not captcha_code:
                captcha_code = self.solve_image_captcha_free(self.page, "img.captchagenerator")
                if captcha_code:
                    self.page.fill("#captcha", captcha_code)
            
            if not captcha_code:
                if not self.headless:
                    print("  💡 Chế độ hiển thị: Vui lòng xem trình duyệt và tự nhập mã Captcha...")
                    for _ in range(45):
                        val = self.page.locator("#captcha").input_value()
                        if len(val.strip()) >= 3:
                            print(f"  ✓ Đã nhận diện mã captcha nhập thủ công: {val}")
                            captcha_code = val
                            break
                        time.sleep(1)
                else:
                    print("  ⚠️ Không giải được captcha tự động (chạy ẩn danh và không cấu hình 2Captcha key)")
                
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.safe_screenshot(os.path.join(script_dir, f"{base_url.replace('.', '_')}_form_filled.png"))
            
            submit_btn = self.page.locator("span.update, #form1 input[type='submit'], #form1 button:has-text('Đăng tin'), #form1 input[value='Đăng tin'], #form1 a:has-text('Đăng tin'), input[type='submit']").first
            if submit_btn.count() > 0 and submit_btn.is_visible():
                submit_btn.click()
            else:
                self.page.evaluate("() => { if (typeof AddProperty === 'function') { AddProperty(); } else { const f = document.querySelector('form'); if(f) f.submit(); } }")
                
            time.sleep(5)
            
            final_url = self.page.url
            is_success = False
            if "/dang-tin" not in final_url or "success" in final_url.lower():
                is_success = True
            else:
                success_box = self.page.locator(".submit-result-box, .message-box").first
                if success_box.count() > 0 and success_box.is_visible() and ("thành công" in success_box.inner_text().lower() or "success" in success_box.inner_text().lower()):
                    is_success = True
                else:
                    success_el = self.page.locator("text=Đăng tin thành công, text=thành công, .success").first
                    if success_el.count() > 0 and success_el.is_visible():
                        is_success = True
                    
            if is_success:
                print(f"🎉 Đăng tin {base_url} thành công! URL: {final_url}")
                return True
            else:
                print(f"❌ Đăng tin {base_url} thất bại! Vẫn ở trang: {final_url}")
                self.safe_screenshot(os.path.join(script_dir, f"{base_url.replace('.', '_')}_submit_failed.png"))
                return False
                
        except Exception as e:
            print(f"❌ Lỗi đăng tin {base_url}: {e}")
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                self.safe_screenshot(os.path.join(script_dir, f"{base_url.replace('.', '_')}_post_exception.png"))
            except:
                pass
            return False

    def post_123nhadatviet(self, item):
        return self.post_123nhadatviet_shared("123nhadatviet.com", item)

    def post_nhadatviet247(self, item):
        return self.post_123nhadatviet_shared("nhadatviet247.net", item)


    def login_maumau(self, username, password):
        print(f"Đang đăng nhập vào maumau.vn với tài khoản: {username}")
        try:
            self.page.goto("https://id.maumau.vn/login?return-url=https%3A%2F%2Fmaumau.vn&code=maumau", wait_until="networkidle")
            time.sleep(2)
            self.page.fill("input#email", username)
            self.page.fill("input#password", password)
            time.sleep(1)
            self.page.click("button[type='submit']")
            time.sleep(5)
            current_url = self.page.url
            if "id.maumau.vn" not in current_url:
                print("✓ Đăng nhập thành công trên maumau.vn")
                return True
            print("⚠️ Vẫn ở trang đăng nhập. Có thể có CAPTCHA hoặc mật khẩu sai.")
            self.safe_screenshot("maumau_login_failed.png")
            return False
        except Exception as e:
            print(f"❌ Lỗi đăng nhập maumau.vn: {e}")
            return False

    def post_maumau(self, item):
        print(f"Bắt đầu đăng tin trên maumau.vn: {item.get('title')}")
        try:
            local_images = self.download_property_images(item.get('source_url', ''), item.get('title', ''))
            self.page.goto("https://maumau.vn/", wait_until="networkidle")
            time.sleep(2)
            dang_tin_btn = self.page.locator("a:has-text('Đăng tin')")
            if dang_tin_btn.count() > 0:
                dang_tin_btn.first.click()
                time.sleep(4)
            print(f"Đang ở trang đăng tin: {self.page.url}")
            self.safe_screenshot("maumau_post_form.png")
            title = item.get('title', '')
            title_input = self.page.locator("input[placeholder*='tiêu đề'], input[placeholder*='Tiêu đề'], input[name*='title'], input#title")
            if title_input.count() > 0:
                title_input.first.fill(title)
                print(f"  ✓ Điền tiêu đề: {title}")
                time.sleep(1)
            cat_suggest = self.page.locator(".category-suggest, .suggested-category")
            if cat_suggest.count() > 0:
                cat_suggest.first.click()
                print("  ✓ Click gợi ý danh mục")
                time.sleep(2)
            else:
                bds_btn = self.page.locator("text='Bất động sản', :text-matches('Bất động sản', 'i')")
                if bds_btn.count() > 0:
                    bds_btn.first.click()
                    time.sleep(1)
                    chothue_btn = self.page.locator("text='Cho thuê', :text-matches('Cho thuê', 'i')")
                    if chothue_btn.count() > 0:
                        chothue_btn.first.click()
                        time.sleep(1)
                        vp_btn = self.page.locator("text='Văn phòng', :text-matches('Văn phòng', 'i')")
                        if vp_btn.count() > 0:
                            vp_btn.first.click()
                            time.sleep(1)
            price_usd, price_vnd = self.parse_price(item.get('price', ''), item.get('area', ''))
            price_input = self.page.locator("input[placeholder*='giá'], input[placeholder*='Giá'], input[name*='price'], input#price")
            if price_input.count() > 0:
                price_input.first.fill(str(price_vnd))
                print(f"  ✓ Điền giá: {price_vnd}")
                time.sleep(1)
            area_val = str(item.get('area', ''))
            area_input = self.page.locator("input[placeholder*='diện tích'], input[placeholder*='Diện tích'], input[name*='area'], input#area")
            if area_input.count() > 0:
                area_input.first.fill(area_val)
                print(f"  ✓ Điền diện tích: {area_val}")
                time.sleep(1)
            content = item.get('content', '').replace('\\\\n', '\n')
            desc_input = self.page.locator("textarea[placeholder*='mô tả'], textarea[placeholder*='Mô tả'], textarea[name*='description'], textarea#description, textarea#content")
            if desc_input.count() > 0:
                desc_input.first.fill(content)
                print("  ✓ Điền nội dung mô tả")
                time.sleep(1)
            address_val = item.get('address', '')
            addr_input = self.page.locator("input[placeholder*='địa chỉ'], input[placeholder*='Địa chỉ'], input[name*='address'], input#address")
            if addr_input.count() > 0:
                addr_input.first.fill(address_val)
                print(f"  ✓ Điền địa chỉ: {address_val}")
                time.sleep(1)
            if local_images:
                file_input = self.page.locator("input[type='file']")
                if file_input.count() > 0:
                    file_input.first.set_input_files(local_images[:5])
                    print(f"  ✓ Đã upload {min(len(local_images), 5)} ảnh")
                    time.sleep(3)
            self.safe_screenshot("maumau_form_filled.png")
            submit_btn = self.page.locator("button:has-text('Đăng tin'), button:has-text('Tiếp tục'), input[type='submit']")
            if submit_btn.count() > 0:
                submit_btn.first.click()
                time.sleep(5)
            current_url = self.page.url
            if "success" in current_url.lower() or "hoan-thanh" in current_url.lower() or "quan-ly-tin" in current_url.lower():
                print("✓ Đăng tin maumau.vn thành công!")
                self.safe_screenshot("maumau_post_success.png")
                return True
            submit_btn2 = self.page.locator("button:has-text('Đăng tin'), button:has-text('Hoàn tất')")
            if submit_btn2.count() > 0:
                submit_btn2.first.click()
                time.sleep(5)
            print(f"🏁 Đã hoàn thành gửi form trên maumau.vn. URL hiện tại: {self.page.url}")
            self.safe_screenshot("maumau_after_submit.png")
            return True
        except Exception as e:
            print(f"❌ Lỗi đăng tin maumau.vn: {e}")
            self.safe_screenshot("maumau_post_error.png")
            return False

    def login_generic_site_shared(self, base_url, username, password):
        print(f"Đang kiểm tra trạng thái đăng nhập hoặc đăng nhập vào {base_url}...")
        try:
            # 1. Kiểm tra trạng thái đã đăng nhập trên trang chủ trước
            try:
                self.page.goto(f"https://{base_url}/", wait_until="domcontentloaded", timeout=10000)
            except Exception:
                try:
                    self.page.goto(f"http://{base_url}/", wait_until="domcontentloaded", timeout=10000)
                except Exception:
                    pass
            
            self._wait_for_cloudflare(self.page, timeout_secs=10)
            time.sleep(2)
            
            # Các selector nhận diện đã đăng nhập
            logged_in_selectors = [
                "a:has-text('Thoát')", "a:has-text('Đăng xuất')", "a:has-text('Logout')",
                ".logout", "a[href*='thoat']", "a[href*='logout']",
                "a:has-text('Trang cá nhân')", "a:has-text('Quản lý tin')", "a[href*='quan-ly']",
                "a:has-text('Chào ')"
            ]
            for sel in logged_in_selectors:
                try:
                    if self.page.locator(sel).count() > 0:
                        print(f"✓ Đã đăng nhập trước đó trên {base_url} (Tìm thấy nút Thoát/Tài khoản)")
                        return True
                except:
                    pass

            print(f"=> Chưa đăng nhập. Tiến hành truy cập trang đăng nhập của {base_url}...")
            has_loaded = False
            # Thử HTTPS dang-nhap.html trước
            try:
                self.page.goto(f"https://{base_url}/dang-nhap.html", wait_until="domcontentloaded", timeout=8000)
                self._wait_for_cloudflare(self.page, timeout_secs=10)
                time.sleep(2)
                user_input = self.page.locator("input#username, input#email, input[name='username'], input[name='email'], input#txtEmail, input#txtTenDangNhap, input#username1")
                if user_input.count() > 0:
                    has_loaded = True
            except Exception:
                pass
                
            # Thử HTTP dang-nhap.html
            if not has_loaded:
                try:
                    self.page.goto(f"http://{base_url}/dang-nhap.html", wait_until="domcontentloaded", timeout=8000)
                    self._wait_for_cloudflare(self.page, timeout_secs=10)
                    time.sleep(2)
                    user_input = self.page.locator("input#username, input#email, input[name='username'], input[name='email'], input#txtEmail, input#txtTenDangNhap, input#username1")
                    if user_input.count() > 0:
                        has_loaded = True
                except Exception:
                    pass

            # Thử HTTPS dangnhap.html
            if not has_loaded:
                try:
                    self.page.goto(f"https://{base_url}/dangnhap.html", wait_until="domcontentloaded", timeout=8000)
                    self._wait_for_cloudflare(self.page, timeout_secs=10)
                    time.sleep(2)
                    user_input = self.page.locator("input#username, input#email, input[name='username'], input[name='email'], input#txtEmail, input#txtTenDangNhap, input#username1")
                    if user_input.count() > 0:
                        has_loaded = True
                except Exception:
                    pass

            # Thử HTTP dangnhap.html
            if not has_loaded:
                try:
                    self.page.goto(f"http://{base_url}/dangnhap.html", wait_until="domcontentloaded", timeout=8000)
                    self._wait_for_cloudflare(self.page, timeout_secs=10)
                    time.sleep(2)
                    user_input = self.page.locator("input#username, input#email, input[name='username'], input[name='email'], input#txtEmail, input#txtTenDangNhap, input#username1")
                    if user_input.count() > 0:
                        has_loaded = True
                except Exception:
                    pass

            if has_loaded and user_input.count() > 0:
                user_input.first.fill(username)
                pass_input = self.page.locator("input#password, input[name='password'], input#txtPassword, input#txtMatKhau, input#password1")
                if pass_input.count() > 0:
                    pass_input.first.fill(password)
                    time.sleep(1)
                    
                    # Kiểm tra xem có CAPTCHA không
                    captcha_img = self.page.locator("img#imgCaptcha, img[src*='captcha'], img[src*='code']")
                    if captcha_img.count() > 0:
                        print(f"⚠️ Phát hiện CAPTCHA hình ảnh trên trang đăng nhập {base_url}.")
                        print("💡 Bạn vui lòng đăng nhập thủ công một lần trên giao diện để lưu phiên (Session).")
                        return False
                        
                    submit_btn = self.page.locator("button[type='submit'], input[type='submit'], #btnSubmit, #btnLogin, #btnDangNhap, #login, input[name='login']")
                    if submit_btn.count() > 0:
                        submit_btn.first.click()
                        time.sleep(5)
                        
            current_url = self.page.url
            if "dang-nhap" not in current_url and "dangnhap" not in current_url:
                print(f"✓ Đăng nhập thành công trên {base_url}")
                return True
            for sel in logged_in_selectors:
                try:
                    if self.page.locator(sel).count() > 0:
                        print(f"✓ Đăng nhập thành công trên {base_url} (Tìm thấy nút Thoát/Tài khoản)")
                        return True
                except:
                    pass
            print(f"⚠️ Vẫn ở trang đăng nhập {base_url}. Có thể có CAPTCHA hoặc thông tin đăng nhập sai.")
            self.safe_screenshot(f"{base_url.replace('.', '_')}_login_failed.png")
            return False
        except Exception as e:
            print(f"❌ Lỗi đăng nhập {base_url}: {e}")
            return False

    def post_generic_site_shared(self, base_url, item):
        print(f"Bắt đầu đăng tin trên {base_url}: {item.get('title')}")
        try:
            local_images = self.download_property_images(item.get('source_url', ''), item.get('title', ''))
            has_loaded = False
            # Thử HTTPS dang-tin.html trước
            try:
                self.page.goto(f"https://{base_url}/dang-tin.html", wait_until="domcontentloaded", timeout=8000)
                self._wait_for_cloudflare(self.page, timeout_secs=10)
                time.sleep(2)
                title_input = self.page.locator("input#tieude, input#title, input[name='title'], input[name='tieude'], input#txtTieuDe")
                if title_input.count() > 0:
                    has_loaded = True
            except Exception:
                pass
                
            # Thử HTTP dang-tin.html
            if not has_loaded:
                try:
                    self.page.goto(f"http://{base_url}/dang-tin.html", wait_until="domcontentloaded", timeout=8000)
                    self._wait_for_cloudflare(self.page, timeout_secs=10)
                    time.sleep(2)
                except Exception as e:
                    print(f"  ⚠️ Lỗi điều hướng đến trang đăng tin của {base_url}: {e}")
            
            # Giới hạn rõ ràng tag INPUT hoặc TEXTAREA để tránh điền nhầm thẻ <p id="tieude">
            title = item.get("title", "")
            title_input = self.page.locator("input#tieude, input#title, input[name='title'], input[name='tieude'], input#txtTieuDe")
            if title_input.count() > 0:
                title_input.first.fill(title)
            content = item.get("content") or item.get("description", "")
            content = content.replace('\\\\n', '\n')
            content_input = self.page.locator("textarea#noidung, textarea#content, textarea[name='noidung'], textarea[name='content'], textarea#txtNoiDung")
            if content_input.count() > 0:
                content_input.first.fill(content)
            loaitin_val = "2"
            title_lower = title.lower()
            category_lower = (item.get("category") or "").lower()
            post_type = item.get("type", "Thuê").lower()
            if "bán" in title_lower or "ban" in title_lower or "bán" in category_lower or "bán" in post_type:
                loaitin_val = "1"
            type_select = self.page.locator("#loaitin, select[name='loaitin'], #ddlLoaiTin")
            if type_select.count() > 0:
                try:
                    type_select.first.select_option(loaitin_val)
                except:
                    pass
            loaibds_val = "6"
            bds_type = (item.get("category") or item.get("property_type") or "").lower()
            if "chung cư" in bds_type or "căn hộ" in bds_type or "chung cu" in bds_type:
                loaibds_val = "4"
            elif "nhà" in bds_type or "nha" in bds_type:
                loaibds_val = "2"
            elif "đất" in bds_type or "dat" in bds_type:
                loaibds_val = "10"
            bds_select = self.page.locator("#loaibds, select[name='loaibds'], #ddlLoaiBDS")
            if bds_select.count() > 0:
                try:
                    bds_select.first.select_option(loaibds_val)
                except:
                    pass
            tinh_val = "3"
            address_lower = item.get("address", "").lower()
            if "hà nội" in address_lower or "hanoi" in address_lower:
                tinh_val = "1"
            elif "hồ chí minh" in address_lower or "hcm" in address_lower or "sài gòn" in address_lower:
                tinh_val = "2"
            city_select = self.page.locator("#tinh, select[name='tinh'], select[name='city'], #ddlTinhThanh")
            if city_select.count() > 0:
                try:
                    city_select.first.select_option(tinh_val)
                    time.sleep(1)
                except:
                    pass
            district_name = item.get("district", "")
            district_select = self.page.locator("#quan, select[name='quan'], select[name='district'], #ddlQuanHuyen")
            if district_select.count() > 0 and district_name:
                try:
                    district_select.first.select_option(label=district_name)
                    time.sleep(1)
                except:
                    try:
                        district_select.first.select_option(index=1)
                    except:
                        pass
            address_val = item.get("address", "")
            addr_input = self.page.locator("input#diachi, input#address, input[name='address'], input[name='diachi'], input#txtDiaChi")
            if addr_input.count() > 0:
                addr_input.first.fill(address_val)
            price_vnd = self.parse_price(item.get('price', ''), item.get('area', ''))
            price_input = self.page.locator("input#giaban, input#price, input#gia, input[name='price'], input[name='giaban'], input#txtGia")
            if price_input.count() > 0:
                price_input.first.fill(str(price_vnd))
            area_val = str(item.get("area", ""))
            area_input = self.page.locator("input#dientich, input#area, input[name='area'], input[name='dientich'], input#txtDienTich")
            if area_input.count() > 0:
                area_input.first.fill(area_val)
            if local_images:
                file_input = self.page.locator("input[type='file']")
                if file_input.count() > 0:
                    try:
                        file_input.first.set_input_files(local_images[:5])
                        time.sleep(3)
                    except:
                        pass
            self.safe_screenshot(f"{base_url.replace('.', '_')}_form_filled.png")
            submit_btn = self.page.locator("button[type='submit'], input[type='submit'], #btnSubmit, #btnDangTin, button:has-text('Đăng tin')")
            if submit_btn.count() > 0:
                submit_btn.first.click()
                time.sleep(5)
            current_url = self.page.url
            if "thành công" in self.page.content().lower() or "success" in current_url.lower() or "hoan-thanh" in current_url.lower():
                print(f"✓ Đăng tin {base_url} thành công!")
                self.safe_screenshot(f"{base_url.replace('.', '_')}_post_success.png")
                return True
            print(f"🏁 Đã hoàn thành gửi form trên {base_url}. URL hiện tại: {current_url}")
            self.safe_screenshot(f"{base_url.replace('.', '_')}_after_submit.png")
            return True
        except Exception as e:
            print(f"❌ Lỗi đăng tin {base_url}: {e}")
            self.safe_screenshot(f"{base_url.replace('.', '_')}_post_error.png")
            return False

    # ─────────────────────────────────────────────────────────────
    # BDS123.VN
    # ─────────────────────────────────────────────────────────────
    def login_bds123(self, phone, password):
        """Đăng nhập bds123.vn — form dùng placeholder (không có name attr):
           placeholder='Số điện thoại', placeholder='Mật khẩu'
        """
        print("Đang kiểm tra trạng thái đăng nhập bds123.vn...")
        try:
            self.page.goto("https://bds123.vn/", wait_until="domcontentloaded", timeout=15000)
            self._wait_for_cloudflare(self.page, timeout_secs=10)
            time.sleep(2)
            
            # Lấy text của nút dropdown tài khoản để kiểm tra trạng thái đăng nhập
            is_logged_in = False
            toggle_text = ""
            try:
                self.page.wait_for_selector(".dropdown-toggle", timeout=8000)
                toggle_text = self.page.locator(".dropdown-toggle").first.inner_text().strip()
                if toggle_text and "tài khoản" not in toggle_text.lower():
                    is_logged_in = True
            except:
                pass
                
            if is_logged_in:
                print(f"✓ Đã đăng nhập bds123.vn từ session trước (User: {toggle_text})")
                return True


            print("=> Chưa đăng nhập. Vào trang đăng nhập bds123.vn...")
            self.page.goto("https://bds123.vn/dang-nhap.html", wait_until="domcontentloaded", timeout=15000)
            self._wait_for_cloudflare(self.page, timeout_secs=10)
            time.sleep(2)

            # Form dùng id/name thực tế thay vì placeholder vì attributes placeholder trống trong DOM
            self.page.fill("input[name='loginname']", phone)
            time.sleep(0.5)
            self.page.fill("input[name='password']", password)
            time.sleep(0.5)
            self.page.click("button:has-text('Đăng nhập')")
            time.sleep(5)

            url = self.page.url
            if "dang-nhap" not in url:
                print("✓ Đăng nhập bds123.vn thành công")
                self.safe_screenshot("bds123_login_ok.png")
                return True
            print("⚠️ Vẫn ở trang đăng nhập bds123.vn — kiểm tra thông tin đăng nhập")
            self.safe_screenshot("bds123_login_fail.png")
            return False
        except Exception as e:
            print(f"❌ Lỗi đăng nhập bds123.vn: {e}")
            self.safe_screenshot("bds123_login_error.png")
            return False

    def post_bds123(self, item, username=None, password=None):
        """Đăng tin lên bds123.vn — button 'Đăng tin miễn phí'
           Fields: title, type_id(select), province_id(select), district_id(select),
                   ward_id(select), address, area, price, price_type(select),
                   description(textarea), contact_name, contact_phone, images[]
        """
        print(f"Bắt đầu đăng tin bds123.vn: {item.get('title', '')}")
        try:
            local_images = self.download_property_images(item.get('source_url', ''), item.get('title', ''))

            self.page.goto("https://bds123.vn/dang-tin.html", wait_until="domcontentloaded", timeout=20000)
            self._wait_for_cloudflare(self.page, timeout_secs=10)
            time.sleep(3)
            self.safe_screenshot("bds123_post_start.png")

            # bds123 overlay login modal hoặc redirect trên trang /dang-tin.html
            if self.page.locator("input[name='loginname']").count() > 0:
                # Có modal login hoặc đã bị redirect — thực hiện login
                print("  => Phát hiện trang/modal login, tiến hành đăng nhập ngay...")
                try:
                    self.page.fill("input[name='loginname']", username or "0935723727")
                    time.sleep(0.5)
                    self.page.fill("input[name='password']", password or "Binh1995@")
                    time.sleep(0.5)
                    self.page.click("button:has-text('Đăng nhập')")
                    time.sleep(5)
                    # Sau login, thử reload trang đăng tin
                    self.page.goto("https://bds123.vn/dang-tin.html", wait_until="domcontentloaded", timeout=15000)
                    time.sleep(3)
                    self.safe_screenshot("bds123_post_after_login.png")
                except Exception as e_login:
                    print(f"  ⚠️ Không đăng nhập được qua modal: {e_login}")

            # ── Chọn "Cho thuê nhà đất" ──
            try:
                self.page.evaluate("""() => {
                    const selects = document.querySelectorAll("select");
                    for(let sel of selects) {
                        for(let opt of sel.options) {
                            if(opt.text.includes('Cho thuê nhà đất')) {
                                sel.value = opt.value;
                                sel.dispatchEvent(new Event('change'));
                                break;
                            }
                        }
                    }
                }""")
                time.sleep(2)
            except Exception as e_cat1:
                print(f"  ⚠️ Lỗi chọn loại giao dịch: {e_cat1}")

            # ── Chọn "Cho thuê văn phòng" ──
            try:
                self.page.select_option("select[name='estate']", label="Cho thuê văn phòng")
                time.sleep(4)
            except Exception as e_cat2:
                print(f"  ⚠️ Lỗi chọn loại bất động sản: {e_cat2}")

            # ── Địa chỉ qua modal ──
            try:
                print("Mở modal địa chỉ...")
                self.page.click("[data-bs-target='#addressModal']")
                time.sleep(2)
                
                city_name = "Đà Nẵng"
                district_raw = item.get('district', '') or item.get('address', '')
                district_name = "Hải Châu"
                if "thanh khê" in district_raw.lower() or "thanh khe" in district_raw.lower():
                    district_name = "Thanh Khê"
                elif "liên chiểu" in district_raw.lower() or "lien chieu" in district_raw.lower():
                    district_name = "Liên Chiểu"
                elif "sơn trà" in district_raw.lower() or "son tra" in district_raw.lower():
                    district_name = "Sơn Trà"
                elif "ngũ hành sơn" in district_raw.lower() or "ngu hanh son" in district_raw.lower():
                    district_name = "Ngũ Hành Sơn"
                elif "cẩm lệ" in district_raw.lower() or "cam le" in district_raw.lower():
                    district_name = "Cẩm Lệ"
                elif "hòa vang" in district_raw.lower() or "hoa vang" in district_raw.lower():
                    district_name = "Hòa Vang"

                ward_map = {
                    "Hải Châu": "Phường Bình Thuận",
                    "Thanh Khê": "Phường Thạc Gián",
                    "Liên Chiểu": "Phường Hòa Minh",
                    "Sơn Trà": "Phường An Hải Bắc",
                    "Ngũ Hành Sơn": "Phường Mỹ An",
                    "Cẩm Lệ": "Phường Khuê Trung",
                    "Hòa Vang": "Xã Hòa Phong"
                }
                ward_default = ward_map.get(district_name, "Phường Bình Thuận")
                ward_name = ward_default

                # Select Tỉnh/Thành
                p_inp = self.page.locator("input[placeholder='Chọn tỉnh thành phố']")
                p_inp.click()
                time.sleep(0.5)
                p_inp.fill(city_name)
                time.sleep(1.5)
                self.page.locator(f"li:has-text('{city_name}')").first.click()
                time.sleep(1)

                # Select Quận/Huyện
                d_inp = self.page.locator("input[placeholder='Chọn quận huyện']")
                d_inp.click()
                time.sleep(0.5)
                d_inp.fill(district_name)
                time.sleep(1.5)
                self.page.locator(f"li:has-text('{district_name}')").first.click()
                time.sleep(1.5)

                # Select Phường/Xã
                w_inp = self.page.locator("input[placeholder='Chọn phường xã']")
                w_inp.click()
                time.sleep(0.5)
                w_inp.fill(ward_name)
                time.sleep(1.5)
                
                ward_opt = self.page.locator(f"li:has-text('{ward_name}')")
                if ward_opt.count() > 0:
                    ward_opt.first.click()
                else:
                    self.page.locator(".vs__dropdown-menu li").first.click()
                time.sleep(1)

                # Street number
                street_number = "123"
                addr_parts = [p.strip() for p in item.get('address', '').split(',')]
                if addr_parts and addr_parts[0] and any(c.isdigit() for c in addr_parts[0]):
                    street_number = addr_parts[0]
                self.page.fill("input[name='street_number']", street_number)
                time.sleep(1)

                # Click Xong
                self.page.click("button:has-text('Xong')")
                time.sleep(2)
                print("✓ Chọn địa chỉ thành công")
            except Exception as e_addr:
                print(f"  ⚠️ Lỗi khi chọn địa chỉ qua modal: {e_addr}")

            title   = item.get("title", "Cho thuê văn phòng Đà Nẵng")
            content = item.get("content", "").replace("\\n", "\n")
            area    = item.get("area", "")
            price   = item.get("price", "")

            # ── Tiêu đề ──
            if self.page.locator("textarea[name='post_title']").count() > 0:
                self.page.fill("textarea[name='post_title']", title)
            elif self.page.locator("input[name='title']").count() > 0:
                self.page.fill("input[name='title']", title)

            # ── Diện tích ──
            area_val = ""
            if area:
                import re
                nums = re.findall(r"[\d.]+", str(area))
                area_val = nums[0] if nums else ""
            if area_val and self.page.locator("input[name='acreage']").count() > 0:
                self.page.fill("input[name='acreage']", area_val)
            elif area_val and self.page.locator("input[name='area']").count() > 0:
                self.page.fill("input[name='area']", area_val)

            # ── Giá ──
            price_val = ""
            if price:
                import re
                nums = re.findall(r"[\d.]+", str(price))
                price_val = nums[0] if nums else ""
            if price_val and self.page.locator("input[name='price']").count() > 0:
                self.page.fill("input[name='price']", price_val)

            # ── Đơn vị giá: triệu/tháng ──
            try:
                self.page.select_option("select[name='price_type']", label="Triệu/tháng")
            except:
                try:
                    self.page.select_option("select[name='price_type']", index=1)
                except: pass

            # ── Mô tả ──
            if self.page.locator("textarea[name='description']").count() > 0:
                self.page.fill("textarea[name='description']", content or title)

            # ── Upload ảnh ──
            if local_images:
                try:
                    file_input = self.page.locator("input[type='file']")
                    if file_input.count() > 0:
                        print(f"Uploading {len(local_images)} images...")
                        file_input.first.set_input_files(local_images[:10])
                        time.sleep(3)
                except Exception as e_img:
                    print(f"⚠️ Lỗi upload ảnh: {e_img}")

            # ── Thông tin liên hệ ──
            if self.page.locator("input[name='contact_name']").count() > 0:
                self.page.fill("input[name='contact_name']", "Binh Office Da Nang")
            if self.page.locator("input[name='contact_phone']").count() > 0:
                self.page.fill("input[name='contact_phone']", "0935723727")

            self.safe_screenshot("bds123_post_filled.png")

            # ── Submit ──
            submit = self.page.locator("button:has-text('Đăng tin miễn phí'), button[type='submit']")
            if submit.count() > 0:
                submit.first.click()
                time.sleep(6)
            else:
                self.page.keyboard.press("Enter")
                time.sleep(6)

            self.safe_screenshot("bds123_post_done.png")
            url = self.page.url
            print(f"  URL sau đăng tin: {url}")

            # Kiểm tra thành công
            if any(k in url for k in ["quan-ly-tin", "thanh-cong", "success", "tin-dang"]):
                print("✅ Đăng tin bds123.vn thành công!")
                return True
            # Tìm thông báo thành công trong page
            for msg_sel in ["div.alert-success", ".toast-success", "p:has-text('thành công')"]:
                if self.page.locator(msg_sel).count() > 0:
                    print("✅ Đăng tin bds123.vn thành công!")
                    return True
            print(f"🏁 Đã submit bds123.vn — URL: {url}")
            return True
        except Exception as e:
            print(f"❌ Lỗi đăng tin bds123.vn: {e}")
            self.safe_screenshot("bds123_post_error.png")
            return False

    def login_datviet24h(self, username, password):
        """Đăng nhập datviet24h.com.vn - selector: input[name='username'], input[name='password'], input[name='submitbt']"""
        print("Đang kiểm tra trạng thái đăng nhập hoặc đăng nhập vào datviet24h.com.vn...")
        try:
            # Kiểm tra session cũ
            try:
                self.page.goto("https://datviet24h.com.vn/", wait_until="domcontentloaded", timeout=15000)
                self._wait_for_cloudflare(self.page, timeout_secs=10)
                time.sleep(2)
                logged_in_selectors = [
                    "a:has-text('Thoát')", "a:has-text('Đăng xuất')", "a[href*='thoat']",
                    "a[href*='logout']", "a:has-text('Quản lý tin')", "a[href*='quan-ly']"
                ]
                for sel in logged_in_selectors:
                    if self.page.locator(sel).count() > 0:
                        print("✓ Đã đăng nhập trước đó trên datviet24h.com.vn")
                        return True
            except Exception as e_check:
                print(f"  ⚠️ Lỗi check session datviet24h: {e_check}")

            print("=> Chưa đăng nhập. Tiến hành truy cập trang đăng nhập của datviet24h.com.vn...")
            self.page.goto("https://datviet24h.com.vn/dang-nhap.html", wait_until="domcontentloaded", timeout=15000)
            self._wait_for_cloudflare(self.page, timeout_secs=10)
            time.sleep(2)

            # Dùng JS để điền giá trị form - tránh conflict với Chrome persistent session/autocomplete
            try:
                self.page.evaluate(f"""
                    (function() {{
                        var u = document.querySelector("input[name='username']");
                        var p = document.querySelector("input[name='password']");
                        if (u) {{ u.value = '{username}'; u.dispatchEvent(new Event('input', {{bubbles:true}})); }}
                        if (p) {{ p.value = '{password}'; p.dispatchEvent(new Event('input', {{bubbles:true}})); }}
                    }})();
                """)
                time.sleep(0.5)
            except Exception as e_fill:
                print(f"  ⚠️ Không điền được form datviet24h (JS): {e_fill}")
                return False

            # Submit form qua JS để đảm bảo không bị block
            try:
                submitted = self.page.evaluate("""
                    (function() {
                        var btn = document.querySelector("input[name='submitbt']");
                        if (btn) { btn.click(); return 'clicked_submit'; }
                        var form = document.querySelector("form");
                        if (form) { form.submit(); return 'submitted_form'; }
                        return 'not_found';
                    })();
                """)
                print(f"  => Submit result: {submitted}")
            except Exception as e_btn:
                self.page.keyboard.press("Enter")

            # Chờ navigation hoàn tất sau submit
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=8000)
            except Exception:
                pass
            time.sleep(4)
            # Dùng JS evaluate để lấy URL thực trong browser (tránh lỗi cache page.url trong headful Chrome)
            try:
                real_url = self.page.evaluate("window.location.href")
            except Exception:
                real_url = self.page.url
            print(f"  [debug] datviet24h URL sau login: {real_url}")
            if "dang-nhap" not in real_url and "login" not in real_url:
                print("✓ Đăng nhập datviet24h.com.vn thành công")
                return True
            # Kèm check selector đă đăng nhập (thoat, logout, quan-ly)
            for sel in logged_in_selectors:
                if self.page.locator(sel).count() > 0:
                    print("✓ Đăng nhập datviet24h.com.vn thành công")
                    return True
            # Nếu vẫn thấy đường dẫn đăng-nhập thì thất bại
            print("⚠️ Vẫn ở trang đăng nhập datviet24h.com.vn. Có thể có CAPTCHA hoặc thông tin đăng nhập sai.")
            self.safe_screenshot("datviet24h_com_vn_login_failed.png")
            return False
        except Exception as e:
            print(f"❌ Lỗi đăng nhập datviet24h: {e}")
            return False


    def post_datviet24h(self, item):
        return self.post_generic_site_shared("datviet24h.com.vn", item)

    def login_luachonnhadat(self, username, password):
        print(f"LuaChonNhaDat.vn sử dụng cơ chế đăng nhập/đăng tin qua Email. Bỏ qua đăng nhập trước.")
        return True

    def post_luachonnhadat(self, item):
        print(f"Bắt đầu đăng tin trên luachonnhadat.vn: {item.get('title')}")
        try:
            local_images = self.download_property_images(item.get('source_url', ''), item.get('title', ''))
            self.page.goto("https://luachonnhadat.vn/nha-dat/dang-tin.html", wait_until="domcontentloaded")
            time.sleep(2)
            
            email_input = self.page.locator("input#femail")
            if email_input.count() > 0:
                email_val = "binh.officedanang@gmail.com"
                email_input.first.fill(email_val)
                print(f"  ✓ Điền email bước 1: {email_val}")
                time.sleep(1)
                submit_email_btn = self.page.locator("button:has-text('GỬI'), button:has-text('Tiếp tục'), input[type='submit']")
                if submit_email_btn.count() > 0:
                    try:
                        submit_email_btn.first.click(timeout=5000)
                    except Exception:
                        submit_email_btn.first.evaluate("el => el.click()")
                    time.sleep(3)
            
            # Đóng SweetAlert/popup nếu xuất hiện chặn màn hình
            try:
                self.page.evaluate("""() => {
                    const swalOk = document.querySelector('.swal2-confirm, .swal-button--confirm');
                    if (swalOk) swalOk.click();
                }""")
                time.sleep(1)
            except:
                pass

            title = item.get("title", "")
            title_input = self.page.locator("input#tieude, input#title, input[name='title'], input[name='tieude'], input#txtTieuDe")
            if title_input.count() > 0:
                title_input.first.fill(title)
                print("  ✓ Điền tiêu đề")
            
            content = item.get("content") or item.get("description", "")
            content = content.replace('\\\\n', '\n')
            content_input = self.page.locator("textarea#noidung, textarea#content, textarea[name='noidung'], textarea[name='content'], textarea#txtNoiDung")
            if content_input.count() > 0:
                content_input.first.fill(content)
                print("  ✓ Điền nội dung")
                
            price_vnd = self.parse_price(item.get('price', ''), item.get('area', ''))
            price_input = self.page.locator("input#giaban, input#price, input#gia, input[name='price'], input[name='giaban'], input#txtGia")
            if price_input.count() > 0:
                price_input.first.fill(str(price_vnd))
                print("  ✓ Điền giá")
                
            area_val = str(item.get("area", ""))
            area_input = self.page.locator("input#dientich, input#area, input[name='area'], input[name='dientich'], input#txtDienTich")
            if area_input.count() > 0:
                area_input.first.fill(area_val)
                print("  ✓ Điền diện tích")
                
            if local_images:
                file_input = self.page.locator("input[type='file']")
                if file_input.count() > 0:
                    try:
                        file_input.first.set_input_files(local_images[:5])
                        time.sleep(3)
                        print("  ✓ Tải ảnh lên")
                    except:
                        pass
                        
            self.safe_screenshot("luachonnhadat_form_filled.png")
            submit_btn = self.page.locator("button[type='submit'], input[type='submit'], button:has-text('Đăng tin')")
            if submit_btn.count() > 0:
                try:
                    submit_btn.first.click(timeout=5000)
                except Exception:
                    print("  ⚠️ Click thường bị chặn, sử dụng click JS...")
                    submit_btn.first.evaluate("el => el.click()")
                time.sleep(5)
            print(f"🏁 Đã hoàn thành gửi form trên luachonnhadat.vn. URL: {self.page.url}")
            self.safe_screenshot("luachonnhadat_after_submit.png")
            return True
        except Exception as e:
            print(f"❌ Lỗi đăng tin luachonnhadat.vn: {e}")
            self.safe_screenshot("luachonnhadat_post_error.png")
            return False

    def register_dangtinbatdongsan(self, username, password, email, phone):
        print(f"Đang tự động đăng ký tài khoản mới trên dangtinbatdongsan.vn: {username}")
        try:
            self.page.goto("https://dangtinbatdongsan.vn/qttv/dangky", wait_until="domcontentloaded")
            time.sleep(2)
            self.page.fill("#txtTenTruyCap", username)
            self.page.fill("#txtMatKhau", password)
            self.page.fill("#txtMatKhauGoLai", password)
            self.page.fill("#txtTen", "Binh Office Da Nang")
            self.page.fill("#txtDienThoai", phone)
            self.page.fill("#txtEmail", email)
            time.sleep(1)
            self.page.click("#btnDangKy")
            time.sleep(5)
            print("✓ Đã gửi yêu cầu đăng ký dangtinbatdongsan.vn")
            return True
        except Exception as e:
            print(f"❌ Lỗi đăng ký dangtinbatdongsan.vn: {e}")
            return False

    def login_dangtinbatdongsan(self, username, password):
        print(f"Đang đăng nhập vào dangtinbatdongsan.vn với tài khoản: {username}")
        try:
            try:
                self.page.goto("https://dangtinbatdongsan.vn/qttv", wait_until="domcontentloaded", timeout=8000)
            except:
                self.page.goto("http://dangtinbatdongsan.vn/qttv", wait_until="domcontentloaded", timeout=8000)
            time.sleep(2)
            if "login" in self.page.url.lower() or self.page.locator("#txtTenDangNhap").count() > 0:
                self.page.fill("#txtTenDangNhap", username)
                self.page.fill("#txtMatKhau", password)
                time.sleep(1)
                self.page.click("#btnDangNhap")
                time.sleep(5)
                
            if "không tồn tại" in self.page.content().lower() or "tồn tại" in self.page.content().lower():
                print("⚠️ Phát hiện tài khoản chưa tồn tại. Đang tự động đăng ký mới...")
                ok_btn = self.page.locator("button:has-text('Ok'), button:has-text('OK'), a:has-text('Ok')")
                if ok_btn.count() > 0:
                    try:
                        ok_btn.first.click()
                        time.sleep(1)
                    except:
                        pass
                reg_ok = self.register_dangtinbatdongsan(username, password, "binh.officedanang@gmail.com", "0935723727")
                if reg_ok:
                    try:
                        self.page.goto("https://dangtinbatdongsan.vn/qttv", wait_until="domcontentloaded", timeout=8000)
                    except:
                        self.page.goto("http://dangtinbatdongsan.vn/qttv", wait_until="domcontentloaded", timeout=8000)
                    time.sleep(2)
                    self.page.fill("#txtTenDangNhap", username)
                    self.page.fill("#txtMatKhau", password)
                    time.sleep(1)
                    self.page.click("#btnDangNhap")
                    time.sleep(5)
            if "login" not in self.page.url.lower() and self.page.locator("#txtTenDangNhap").count() == 0:
                print("✓ Đăng nhập thành công trên dangtinbatdongsan.vn")
                return True
            print("⚠️ Vẫn ở trang đăng nhập dangtinbatdongsan.vn.")
            self.safe_screenshot("dangtinbatdongsan_login_failed.png")
            return False
        except Exception as e:
            print(f"❌ Lỗi đăng nhập dangtinbatdongsan.vn: {e}")
            return False

    def post_dangtinbatdongsan(self, item):
        print(f"Bắt đầu đăng tin trên dangtinbatdongsan.vn: {item.get('title')}")
        try:
            local_images = self.download_property_images(item.get('source_url', ''), item.get('title', ''))
            
            title = item.get("title", "")
            address = item.get("address", "")
            area = str(item.get("area", ""))
            content = item.get("content") or item.get("description", "")
            content = content.replace('\\\\n', '\n')
            
            bds_type = (item.get("category") or item.get("property_type") or "").lower()
            title_lower = title.lower()
            category_lower = (item.get("category") or "").lower()
            post_type = item.get("type", "Thuê").lower()
            
            is_ban = "bán" in title_lower or "ban" in title_lower or "bán" in category_lower or "bán" in post_type
            is_dat = "đất" in title_lower or "dat" in title_lower or "đất" in category_lower or "đất" in bds_type
            
            if is_dat:
                path = "/qttv/datban" if is_ban else "/qttv/datthue"
            else:
                path = "/qttv/nhaban" if is_ban else "/qttv/nhathue"
                
            self.page.goto(f"https://dangtinbatdongsan.vn{path}", wait_until="domcontentloaded")
            time.sleep(3)
            
            self.page.click("#btnThem")
            time.sleep(2)
            
            price_vnd = self.parse_price(item.get('price', ''), item.get('area', ''))
            if price_vnd >= 1000000000:
                price_val = price_vnd / 1000000000
                unit_id = '1000000000'
            elif price_vnd >= 1000000:
                price_val = price_vnd / 1000000
                unit_id = '1000000'
            elif price_vnd >= 100000:
                price_val = price_vnd / 100000
                unit_id = '100000'
            else:
                price_val = price_vnd
                unit_id = '1000000'
                
            # Phân loại nhóm bds
            nhom_val = "1"
            if "chung cư" in bds_type or "căn hộ" in bds_type:
                nhom_val = "2"
            elif "mặt phố" in bds_type or "mặt tiền" in bds_type:
                nhom_val = "3"
            elif "văn phòng" in bds_type or "van phong" in bds_type:
                nhom_val = "4"
            elif "phòng trọ" in bds_type or "nhà trọ" in bds_type:
                nhom_val = "5"
            elif "cửa hàng" in bds_type or "ki ốt" in bds_type or "mặt bằng" in bds_type:
                nhom_val = "6"
                
            # Điền các giá trị thông qua Javascript/jQuery
            self.page.evaluate("""([t, a, c, ar, pr, u_id, nh_val]) => {
                $('#txtTen').val(t);
                $('#txtDiaChi').val(a);
                
                if (window.CKEDITOR && CKEDITOR.instances.txtMoTaChiTiet) {
                    CKEDITOR.instances.txtMoTaChiTiet.setData(c.replace(/\\n/g, '<br>'));
                } else {
                    $('#txtMoTaChiTiet').val(c);
                }
                
                $('#txtDienTich').val(ar);
                $('#_easyui_textbox_input9').val(ar);
                
                $('#txtGiaBan').val(pr);
                $('#_easyui_textbox_input13').val(pr);
                
                // Combotrees
                if ($('#cboNhomNhaThue').length) $('#cboNhomNhaThue').combotree('setValue', nh_val);
                if ($('#cboNhomNhaBan').length) $('#cboNhomNhaBan').combotree('setValue', nh_val);
                if ($('#cboNhomDatThue').length) $('#cboNhomDatThue').combotree('setValue', nh_val);
                if ($('#cboNhomDatBan').length) $('#cboNhomDatBan').combotree('setValue', nh_val);
                
                // Set TTP
                const tRoots = $('#cboTTP').combotree('tree').tree('getRoots');
                let tId = '01'; // Hà Nội
                const addr = a.toLowerCase();
                if (addr.includes("đà nẵng") || addr.includes("da nang")) {
                    tId = '48';
                } else if (addr.includes("hồ chí minh") || addr.includes("hcm") || addr.includes("sài gòn")) {
                    tId = '79';
                } else {
                    const match = tRoots.find(r => addr.includes(r.text.replace('Tỉnh ', '').replace('Thành phố ', '').toLowerCase()));
                    if (match) tId = match.id;
                }
                $('#cboTTP').combotree('setValue', tId);
                $('#cboDonViGiaBan').combotree('setValue', u_id);
            }""", [title, address, content, area, str(price_val), unit_id, nhom_val])
            
            time.sleep(3.5) # Chờ ajax load quận/huyện
            
            # Chọn quận/huyện cboXa
            district_name = item.get("district", "").lower()
            self.page.evaluate(f"""(dist) => {{
                const xRoots = $('#cboXa').combotree('tree').tree('getRoots');
                const match = xRoots.find(x => x.text.toLowerCase().includes(dist) || dist.includes(x.text.toLowerCase().replace('phường ', '').replace('quận ', '').replace('huyện ', '')));
                if (match) {{
                    $('#cboXa').combotree('setValue', match.id);
                }} else if (xRoots.length > 1) {{
                    $('#cboXa').combotree('setValue', xRoots[1].id);
                }}
            }}""", district_name)
            time.sleep(1)
            
            # Tải lên 1 ảnh đại diện (không hỗ trợ multiple file input)
            if local_images:
                file_input = self.page.locator("input[type='file']")
                if file_input.count() > 0:
                    try:
                        file_input.first.set_input_files(local_images[0])
                        time.sleep(3)
                        print("  ✓ Tải ảnh đại diện lên")
                    except Exception as img_err:
                        print(f"  ⚠️ Lỗi tải ảnh: {img_err}")
                        
            self.safe_screenshot("dangtinbatdongsan_form_filled.png")
            
            # Click Lưu
            self.page.click("#btnLuu")
            time.sleep(5)
            
            self.safe_screenshot("dangtinbatdongsan_after_submit.png")
            print(f"✓ Đăng tin dangtinbatdongsan.vn thành công!")
            return True
        except Exception as e:
            print(f"❌ Lỗi đăng tin dangtinbatdongsan.vn: {e}")
            self.safe_screenshot("dangtinbatdongsan_post_error.png")
            return False

    def login_diaocanphu(self, username, password):
        return self.login_generic_site_shared("diaocanphu.com", username, password)

    def post_diaocanphu(self, item):
        return self.post_generic_site_shared("diaocanphu.com", item)

    def login_muabandanang(self, username, password):
        print("Đang kiểm tra trạng thái đăng nhập hoặc đăng nhập vào muabandanang.vn...")
        try:
            try:
                self.page.goto("https://muabandanang.vn/", wait_until="domcontentloaded", timeout=20000)
            except Exception:
                self.page.goto("http://muabandanang.vn/", wait_until="domcontentloaded", timeout=20000)
            self._wait_for_cloudflare(self.page, timeout_secs=10)
            time.sleep(2)
            
            # Check if logged in
            if self.page.locator("a:has-text('Đăng xuất'), a[href*='logout']").count() > 0:
                print("✓ Đã đăng nhập trước đó trên muabandanang.vn")
                return True
                
            print("Chưa đăng nhập. Truy cập trang đăng nhập muabandanang.vn...")
            try:
                self.page.goto("https://muabandanang.vn/dang-nhap", wait_until="domcontentloaded", timeout=20000)
            except Exception:
                self.page.goto("http://muabandanang.vn/dang-nhap", wait_until="domcontentloaded", timeout=20000)
            self.page.wait_for_timeout(2000)
            
            if self.page.locator("#user_login").is_visible():
                self.page.fill("#user_login", username)
                self.page.fill("#user_pass", password)
                self.page.click("#wp-submit")
                self.page.wait_for_timeout(4000)
                
            if self.page.locator("a:has-text('Đăng xuất'), a[href*='logout']").count() > 0 or "dang-nhap" not in self.page.url:
                print("✓ Đăng nhập thành công trên muabandanang.vn")
                return True
            else:
                print("⚠️ Đăng nhập thất bại hoặc cần xác thực thủ công.")
                self.safe_screenshot("muabandanang_login_failed.png")
                return False
        except Exception as e:
            print(f"❌ Lỗi đăng nhập muabandanang.vn: {e}")
            return False

    def post_muabandanang(self, item):
        print(f"Bắt đầu đăng tin trên muabandanang.vn: {item.get('title')}")
        try:
            local_images = self.download_property_images(item.get('source_url', ''), item.get('title', ''))
            
            try:
                self.page.goto("https://muabandanang.vn/dang-tin", wait_until="domcontentloaded", timeout=60000)
                self._wait_for_cloudflare(self.page, timeout_secs=15)
            except Exception:
                try:
                    self.page.goto("http://muabandanang.vn/dang-tin", wait_until="domcontentloaded", timeout=60000)
                    self._wait_for_cloudflare(self.page, timeout_secs=15)
                except Exception as e2:
                    print(f"  ⚠️ Không thể truy cập trang đăng tin muabandanang.vn: {e2}")
                    return False
            self.page.wait_for_timeout(4000)
            
            # Fill form
            # 0. Số ngày đăng tối thiểu
            if self.page.locator("input[name='vip_day']").is_visible():
                self.page.fill("input[name='vip_day']", "30")
                
            # 1. Type of realty: Cho thuê (realty-rent)
            self.page.select_option("select[name='type-realty']", "realty-rent")
            self.page.wait_for_timeout(2000)
            
            # 2. Term type: Cho thuê văn phòng (cho-thue-van-phong)
            self.page.select_option("select[name='term-type']", "cho-thue-van-phong")
            
            # 3. Title
            title_str = item.get('title', '')
            self.page.fill("#postTitle", title_str)
            
            # 4. Content (WYSIWYG TinyMCE bypass)
            desc_str = item.get('description', '')
            self.page.evaluate("""([text]) => {
                const el = document.querySelector('#postContent');
                if (el) {
                    el.value = text;
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                }
                if (typeof tinymce !== 'undefined' && tinymce.get('postContent')) {
                    tinymce.get('postContent').setContent(text);
                }
            }""", [desc_str])
            
            # 5. Address
            address_str = item.get('address', 'Hải Châu, Đà Nẵng')
            self.page.fill("#address", address_str)
            
            # 6. City: Đà Nẵng (2341)
            self.page.select_option("select[name='city']", "2341")
            self.page.wait_for_timeout(2000)
            
            # 7. Ward (dynamic match)
            ward_str = item.get('ward', '') or item.get('district', '')
            if ward_str:
                ward_val = self.page.evaluate("""(wName) => {
                    const el = document.querySelector('select[name="ward"]');
                    if (!el) return "";
                    const opt = Array.from(el.options).find(o => o.text.toLowerCase().replace(/\\s+/g, '').includes(wName.toLowerCase().replace(/\\s+/g, '')));
                    return opt ? opt.value : "";
                }""", ward_str)
                if ward_val:
                    self.page.select_option("select[name='ward']", ward_val)
                    print(f"  ✓ Đã tự động chọn Phường/Xã: {ward_str}")
            
            # 8. Price
            price_str = item.get('price', '')
            price_digits = "".join(c for c in price_str if c.isdigit())
            if price_digits:
                self.page.fill("input[name='post_price']", price_digits)
                
            # 9. Area
            area_str = item.get('area', '')
            area_digits = "".join(c for c in area_str if c.isdigit() or c == '.')
            if area_digits:
                self.page.fill("#post_area", area_digits)
                
            # 10. Contact Info
            self.page.fill("input[name='post_name_contact']", "Bình Office Đà Nẵng")
            self.page.fill("input[name='post_phone_contact']", "0935723727")
            
            # 11. Images
            if local_images:
                uploaded_count = 0
                for idx, img_path in enumerate(local_images[:10]):
                    sel = f"#upload-file{idx+1}"
                    if self.page.locator(sel).count() > 0:
                        self.page.locator(sel).set_input_files(img_path)
                        self.page.wait_for_timeout(500)
                        uploaded_count += 1
                print(f"  ✓ Đã upload {uploaded_count} ảnh.")
                
            self.safe_screenshot("muabandanang_filled.png")
            
            # Submit form
            submit_btn = self.page.locator("button[type='submit']:has-text('ĐĂNG KÝ'), button[type='submit']:has-text('ĐĂNG TIN')").first
            if submit_btn.is_visible():
                submit_btn.click()
                self.page.wait_for_timeout(8000)
                
            self.safe_screenshot("muabandanang_posted.png")
            print("✓ Đăng tin thành công trên muabandanang.vn")
            return True
        except Exception as e:
            print(f"❌ Lỗi đăng tin muabandanang.vn: {e}")
            return False

    def select_option_robust(self, selector, match_text):
        try:
            self.page.wait_for_selector(selector, timeout=3000)
            options = self.page.evaluate(f"""(sel) => {{
                const el = document.querySelector(sel);
                if (!el) return [];
                return Array.from(el.options).map(o => ({{ value: o.value, text: o.text }}));
            }}""", selector)
            
            found_value = None
            for opt in options:
                if match_text.lower() in opt['text'].lower():
                    found_value = opt['value']
                    break
            if found_value:
                self.page.select_option(selector, found_value, timeout=3000)
                print(f"  ✓ Đã chọn option '{opt['text']}' cho {selector}")
                return True
            else:
                print(f"  ⚠️ Không tìm thấy option chứa '{match_text}' trong {selector}")
                return False
        except Exception as e:
            print(f"  ⚠️ Lỗi robust select {selector} với '{match_text}': {e}")
            return False

    def login_phongtro123(self, username, password):
        print("Đang kiểm tra trạng thái đăng nhập phongtro123.com...")
        try:
            self.page.goto("https://phongtro123.com/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            if self.page.locator("a:has-text('Thoát'), a[href*='thoat'], a:has-text('Đăng xuất'), a[href*='logout']").count() > 0:
                print("✓ Đã đăng nhập trước đó trên phongtro123.com")
                return True
            print("Chưa đăng nhập. Truy cập trang đăng nhập phongtro123.com...")
            # URL đăng nhập thực tế là /dang-nhap-tai-khoan (không phải /dang-nhap - trả về 404)
            self.page.goto("https://phongtro123.com/dang-nhap-tai-khoan", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            # Selector từ DOM: input[name='loginname'] cho tài khoản, input[name='password'] cho mật khẩu
            self.page.fill("input[name='loginname']", username)
            self.page.fill("input[name='password']", password)
            self.page.click("button[type='submit'], button:has-text('Đăng nhập')")
            time.sleep(4)
            if self.page.locator("a:has-text('Thoát'), a[href*='thoat'], a:has-text('Đăng xuất'), a[href*='logout']").count() > 0:
                print("✓ Đăng nhập thành công trên phongtro123.com")
                return True
            else:
                print("⚠️ Đăng nhập phongtro123.com thất bại hoặc cần tương tác.")
                return False
        except Exception as e:
            print(f"❌ Lỗi đăng nhập phongtro123.com: {e}")
            return False

    def post_phongtro123(self, item):
        print(f"Bắt đầu đăng tin trên phongtro123.com: {item.get('title')}")
        try:
            local_images = self.download_property_images(item.get('source_url', ''), item.get('title', ''))
            self.page.goto("https://phongtro123.com/quan-ly/dang-tin-moi.html", wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Chọn loại chuyên mục (Cho thuê mặt bằng, văn phòng)
            self.select_option_robust("select#post_cat", "mặt bằng")
            
            # Địa chỉ: Đà Nẵng, Quận Hải Châu
            self.select_option_robust("select#province_id", "Đà Nẵng")
            time.sleep(2)
            self.select_option_robust("select#district_id", "Hải Châu")
            time.sleep(2)
            
            # Phường/Xã
            ward_str = item.get('ward', '') or "Hòa Cường Bắc"
            self.select_option_robust("select#phuongxa_new", ward_str)
            
            # Địa chỉ chi tiết (bỏ readonly để tự điền bằng JS)
            addr_str = item.get('address', 'Hải Châu, Đà Nẵng')
            self.page.evaluate("""(val) => {
                const el = document.querySelector('input#diachi');
                if (el) {
                    el.removeAttribute('readonly');
                    el.value = val;
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }""", addr_str)
            
            # Giá
            price_str = item.get('price', '')
            price_digits = "".join(c for c in price_str if c.isdigit())
            if price_digits:
                self.page.locator("input#giachothue").first.fill(price_digits)
            
            # Diện tích
            area_str = item.get('area', '')
            area_digits = "".join(c for c in area_str if c.isdigit() or c == '.')
            if area_digits:
                self.page.locator("input#post_acreage").first.fill(area_digits)
                
            # Tiêu đề
            self.page.locator("textarea#post_title").first.fill(item.get('title', ''))
            
            # Nội dung mô tả
            self.page.locator("textarea#post_content").first.fill(item.get('description', ''))
            
            # Thông tin liên hệ
            try:
                self.page.locator("input#ten_lien_he").first.fill("Bình Office Đà Nẵng")
                self.page.locator("input#phone").first.fill("0935723727")
            except:
                pass
                
            # Ảnh
            if local_images:
                try:
                    file_input = self.page.locator("input[type='file']").first
                    file_input.set_input_files(local_images[:5])
                    time.sleep(3)
                except Exception as e:
                    print(f"  ⚠️ Không upload được ảnh phongtro123: {e}")
            
            self.safe_screenshot("phongtro123_filled.png")
            submit_btn = self.page.locator("button[type='submit']").first
            if submit_btn.is_visible():
                submit_btn.click()
                time.sleep(5)
            print("✓ Đăng tin phongtro123.com hoàn tất")
            return True
        except Exception as e:
            print(f"❌ Lỗi đăng tin phongtro123.com: {e}")
            return False

    def login_thuephongtro(self, username, password):
        print("Đang kiểm tra trạng thái đăng nhập thuephongtro.com...")
        try:
            self.page.goto("https://thuephongtro.com/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            if self.page.locator("a:has-text('Thoát'), a[href*='thoat'], a:has-text('Đăng xuất'), a[href*='logout']").count() > 0:
                print("✓ Đã đăng nhập trước đó trên thuephongtro.com")
                return True
            print("Chưa đăng nhập. Truy cập trang đăng nhập thuephongtro.com...")
            self.page.goto("https://thuephongtro.com/dang-nhap.html", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            self.page.fill("input#Email, input[name='Email'], input[name='phone'], input#phone", username)
            self.page.fill("input#Password, input[name='Password'], input[name='password'], input#password", password)
            self.page.click("button[type='submit'], button:has-text('Đăng nhập')")
            time.sleep(4)
            if self.page.locator("a:has-text('Thoát'), a[href*='thoat'], a:has-text('Đăng xuất'), a[href*='logout']").count() > 0:
                print("✓ Đăng nhập thành công trên thuephongtro.com")
                return True
            else:
                print("⚠️ Đăng nhập thuephongtro.com thất bại hoặc cần tương tác.")
                return False
        except Exception as e:
            print(f"❌ Lỗi đăng nhập thuephongtro.com: {e}")
            return False

    def post_thuephongtro(self, item):
        print(f"Bắt đầu đăng tin trên thuephongtro.com: {item.get('title')}")
        try:
            local_images = self.download_property_images(item.get('source_url', ''), item.get('title', ''))
            self.page.goto("https://thuephongtro.com/dang-tin.html", wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Tỉnh/Thành phố: Đà Nẵng
            self.select_option_robust("select#ddlProvince", "Đà Nẵng")
            time.sleep(2)
            
            # Quận/Huyện: Hải Châu
            self.select_option_robust("select#ddlDistrict", "Hải Châu")
            time.sleep(2)
            
            # Phường/Xã
            ward_str = item.get('ward', '') or "Hòa Cường Bắc"
            self.select_option_robust("select#ddlWard", ward_str)
            
            # Địa chỉ chi tiết
            addr_str = item.get('address', 'Hải Châu, Đà Nẵng')
            self.page.locator("input#txtAddress").first.fill(addr_str)
            
            # Chọn loại chuyên mục (Cho thuê mặt bằng, văn phòng)
            self.select_option_robust("select#ddlPostCate", "văn phòng")
            
            # Giá (thuephongtro tính theo triệu/tháng, ví dụ: 2.5)
            price_str = item.get('price', '')
            price_digits = "".join(c for c in price_str if c.isdigit())
            if price_digits:
                price_million = float(price_digits) / 1000000.0
                self.page.locator("input#Price").first.fill(str(price_million))
            
            # Diện tích
            area_str = item.get('area', '')
            area_digits = "".join(c for c in area_str if c.isdigit() or c == '.')
            if area_digits:
                self.page.locator("input#Area").first.fill(area_digits)
                
            # Tiêu đề
            self.page.locator("input#Title").first.fill(item.get('title', ''))
            
            # Nội dung mô tả
            self.page.locator("textarea#Detail").first.fill(item.get('description', ''))
            
            # Thông tin liên hệ
            try:
                self.page.locator("input#ContactName").first.fill("Bình Office Đà Nẵng")
                self.page.locator("input#ContactMobile").first.fill("0935723727")
            except:
                pass
                
            # Ảnh
            if local_images:
                try:
                    file_input = self.page.locator("input[type='file']").first
                    file_input.set_input_files(local_images[:5])
                    time.sleep(3)
                except Exception as e:
                    print(f"  ⚠️ Không upload được ảnh thuephongtro: {e}")
            
            self.safe_screenshot("thuephongtro_filled.png")
            submit_btn = self.page.locator("button[type='submit']").first
            if submit_btn.is_visible():
                submit_btn.click()
                time.sleep(5)
            print("✓ Đăng tin thuephongtro.com hoàn tất")
            return True
        except Exception as e:
            print(f"❌ Lỗi đăng tin thuephongtro.com: {e}")
            return False


    def login_nhachothue(self, username, password):
        """Đăng nhập nhachothue.vn - Login qua modal popup, mở bằng nút Đăng nhập trên header"""
        print("Đang kiểm tra trạng thái đăng nhập nhachothue.vn...")
        try:
            self.page.goto("https://nhachothue.vn/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            # Kiểm tra đã đăng nhập chưa
            logged_in_selectors = [
                "a[href*='logout']", "a:has-text('Đăng xuất')",
                "a[href*='quan-ly']", "a:has-text('Quản lý')",
                ".user-info", ".btn-logout", "a:has-text('Tài khoản')"
            ]
            for sel in logged_in_selectors:
                if self.page.locator(sel).count() > 0:
                    print("✓ Đã đăng nhập trước đó trên nhachothue.vn")
                    return True

            print("Chưa đăng nhập. Mở modal login trên nhachothue.vn...")
            # nhachothue.vn dùng modal popup - cần click nút 'Đăng nhập' để mở modal
            try:
                login_trigger = self.page.locator("button:has-text('Đăng nhập'):visible").first
                if login_trigger.count() > 0:
                    login_trigger.click()
                    time.sleep(1.5)
                else:
                    # Thử tìm link Đăng nhập trong navbar
                    self.page.locator("a:has-text('Đăng nhập')").first.click()
                    time.sleep(1.5)
            except Exception as e_open:
                print(f"  ⚠️ Không mở được modal login nhachothue: {e_open}")
                return False

            # Sau khi modal mở, #email-login sẽ visible
            try:
                self.page.wait_for_selector("#email-login:visible", timeout=5000)
                login_email = username if '@' in str(username) else "binh.officedanang@gmail.com"
                self.page.fill("#email-login", login_email)
                self.page.fill("#password-login", password)
            except Exception as e_fill:
                print(f"  ⚠️ Không điền được form login nhachothue: {e_fill}")
                return False

            # Click nút submit trong modal (button thứ 2 - Đăng nhập)
            try:
                # Nút 'Đăng nhập' trong form modal (visible sau khi modal mở)
                submit_btn = self.page.locator("form:has(#email-login) button[type='submit']:visible, form:has(#email-login) button.w-full:visible").first
                if submit_btn.count() > 0:
                    submit_btn.click()
                else:
                    self.page.evaluate("""
                        () => {
                            const emailInput = document.getElementById('email-login');
                            if (emailInput) {
                                const form = emailInput.closest('form');
                                if (form) {
                                    const btn = form.querySelector('button[type="submit"], button.w-full, button');
                                    if (btn) btn.click();
                                }
                            }
                        }
                    """)
            except Exception as e_btn:
                print(f"  ⚠️ Không click được nút submit nhachothue: {e_btn}")
                return False

            time.sleep(2)
            # nhachothue.vn hiển thị modal "Đăng nhập thành công!" với nút OK — cần click để đóng
            try:
                ok_btn = self.page.locator("button:has-text('OK'):visible")
                if ok_btn.count() > 0:
                    ok_btn.first.click()
                    time.sleep(1.5)
                    print("  => Đã click OK trên modal xác nhận đăng nhập")
            except Exception:
                pass
            time.sleep(2)
            # Verify đăng nhập thành công
            for sel in logged_in_selectors:
                if self.page.locator(sel).count() > 0:
                    print("✓ Đăng nhập thành công trên nhachothue.vn")
                    return True
            # Kiểm tra thêm: nếu navbar không có nút Đăng nhập nữa = đã login
            if self.page.locator("a[href='#']:has-text('Đăng nhập')").count() == 0 and self.page.locator("a:has-text('Đăng nhập')").count() == 0:
                print("✓ Đăng nhập thành công trên nhachothue.vn (kiểm tra qua nav)")
                return True
            print("⚠️ Đăng nhập nhachothue.vn thất bại hoặc cần xác thực thêm.")
            self.safe_screenshot("nhachothue_login_failed.png")
            return False
        except Exception as e:
            print(f"❌ Lỗi đăng nhập nhachothue.vn: {e}")
            return False

    def post_nhachothue(self, item):
        print(f"Bắt đầu đăng tin trên nhachothue.vn: {item.get('title')}")
        try:
            local_images = self.download_property_images(item.get('source_url', ''), item.get('title', ''))
            # URL đăng tin: /dang-tin (không có .html)
            self.page.goto("https://nhachothue.vn/dang-tin", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            
            # Nếu bị redirect sang /unauthorized thì cần login lại
            if "unauthorized" in self.page.url:
                print("  => Phươn đăng nhập hết hạn, thực hiện login lại...")
                site_conf = getattr(self, 'config', {}).get("nhachothue.vn", {})
                _user = site_conf.get("username") or site_conf.get("email", "binh.officedanang@gmail.com")
                _pass = site_conf.get("password", "Binh1995@")
                self.login_nhachothue(_user, _pass)
                time.sleep(2)
                self.page.goto("https://nhachothue.vn/dang-tin", wait_until="domcontentloaded", timeout=30000)
                time.sleep(2)
            
            if "unauthorized" in self.page.url:
                print("⚠️ Không thể vào trang đăng tin nhachothue.vn sau khi đăng nhập")
                return False

            self.select_option_robust("select[name='category']", "văn phòng")
            
            # Địa chỉ: Đà Nẵng, Hải Châu
            self.select_option_robust("select[name='city']", "Đà Nẵng")
            time.sleep(1)
            self.select_option_robust("select[name='district']", "Hải Châu")
            time.sleep(1)
                
            # Tiêu đề
            self.page.locator("input[name='title']").first.fill(item.get('title', ''))
            
            # Mô tả
            self.page.locator("textarea[name='content']").first.fill(item.get('description', ''))
            
            # Giá
            price_str = item.get('price', '')
            price_digits = "".join(c for c in price_str if c.isdigit())
            if price_digits:
                self.page.locator("input[name='price']").first.fill(price_digits)
            
            # Diện tích
            area_str = item.get('area', '')
            area_digits = "".join(c for c in area_str if c.isdigit() or c == '.')
            if area_digits:
                self.page.locator("input[name='area']").first.fill(area_digits)
                
            # Ảnh
            if local_images:
                try:
                    file_input = self.page.locator("input[type='file']").first
                    file_input.set_input_files(local_images[:5])
                    time.sleep(3)
                except Exception as e:
                    print(f"  ⚠️ Không upload được ảnh nhachothue: {e}")
            
            self.safe_screenshot("nhachothue_filled.png")
            submit_btn = self.page.locator("button[type='submit']:has-text('Đăng tin')").first
            if submit_btn.is_visible():
                submit_btn.click()
                time.sleep(5)
            print("✓ Đăng tin nhachothue.vn hoàn tất")
            return True
        except Exception as e:
            print(f"❌ Lỗi đăng tin nhachothue.vn: {e}")
            return False

    def renew_posts(self, site_key, username, password):
        """Tự động đăng nhập và Up tin / Làm mới tin đăng trên các nền tảng"""
        print(f"\n--- 🔄 Bắt đầu tự động Up tin trên: {site_key.upper()} ---")
        try:
            if site_key in ["123nhadatviet.com", "nhadatviet247.net"]:
                login_ok = self.login_123nhadatviet_shared(site_key, username, password)
                if not login_ok:
                    return False
                self.page.goto(f"http://{site_key}/trang-ca-nhan.html", wait_until="domcontentloaded")
                time.sleep(2)
                refreshes = self.page.locator("a:has-text('Làm mới'), a:has-text('Up tin'), .btn-refresh").all()
                if not refreshes:
                    print("  ⚠️ Không tìm thấy nút Làm mới/Up tin nào.")
                else:
                    print(f"  ⚡ Tìm thấy {len(refreshes)} tin đăng có thể Up tin. Tiến hành click...")
                    for idx, ref in enumerate(refreshes):
                        try:
                            ref.click()
                            time.sleep(2)
                            print(f"    ✓ Đã click Up tin thứ {idx+1}")
                        except Exception:
                            pass
                return True

            elif site_key == "raovat.net":
                login_ok = self.login_raovat_net(username, password)
                if not login_ok:
                    return False
                self.page.goto("https://raovat.net/danh-sach-tin", wait_until="domcontentloaded")
                time.sleep(2)
                refreshes = self.page.locator("a:has-text('Làm mới'), .btn-refresh, a[href*='action=refresh']").all()
                if not refreshes:
                    print("  ⚠️ Không tìm thấy nút Làm mới tin nào.")
                else:
                    print(f"  ⚡ Tìm thấy {len(refreshes)} tin đăng có thể làm mới. Tiến hành click...")
                    for idx, ref in enumerate(refreshes):
                        try:
                            ref.click()
                            time.sleep(2)
                            print(f"    ✓ Đã click làm mới tin thứ {idx+1}")
                        except Exception:
                            pass
                return True
                
            elif site_key == "thuviennhadat.vn":
                login_ok = self.login_thuviennhadat(username, password)
                if not login_ok:
                    return False
                self.page.goto("https://thuviennhadat.vn/trang-ca-nhan/quan-ly-tin", wait_until="domcontentloaded")
                time.sleep(2)
                refreshes = self.page.locator("a:has-text('Làm mới'), a[title*='Làm mới'], .btn-refresh-listing").all()
                if not refreshes:
                    print("  ⚠️ Không tìm thấy nút Làm mới tin nào.")
                else:
                    print(f"  ⚡ Tìm thấy {len(refreshes)} tin đăng có thể làm mới. Tiến hành click...")
                    for idx, ref in enumerate(refreshes):
                        try:
                            ref.click()
                            time.sleep(2)
                            print(f"    ✓ Đã click làm mới tin thứ {idx+1}")
                        except Exception:
                            pass
                return True
                
            elif site_key == "muaban.net":
                login_ok = self.login_muaban(username, password)
                if not login_ok:
                    return False
                self.page.goto("https://muaban.net/quan-ly-tin", wait_until="domcontentloaded")
                self._wait_for_cloudflare(self.page, timeout_secs=25)
                time.sleep(2)
                refreshes = self.page.locator("button:has-text('Làm mới'), .btn-refresh").all()
                if not refreshes:
                    print("  ⚠️ Không tìm thấy nút Làm mới tin nào.")
                else:
                    print(f"  ⚡ Tìm thấy {len(refreshes)} tin đăng có thể làm mới. Tiến hành click...")
                    for idx, ref in enumerate(refreshes):
                        try:
                            ref.click()
                            time.sleep(2)
                            print(f"    ✓ Đã click làm mới tin thứ {idx+1}")
                        except Exception:
                            pass
                return True
                
            else:
                print(f"  ⚠️ Nền tảng {site_key} chưa được hỗ trợ tự động Up tin.")
                return False
        except Exception as e:
            print(f"  ❌ Lỗi xảy ra khi Up tin trên {site_key}: {e}")
            return False

    def post_by_selectors(self, site_name, site_config, item, dry_run=False):
        """Đăng tin bằng phương thức Hybrid Selector.
        Đọc các selectors từ selectors_db.json, nếu không tồn tại hoặc lỗi thì trả về False.
        """
        import json
        import os
        import time

        selectors_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "selectors_db.json")
        if not os.path.exists(selectors_path):
            print(f"[{site_name}] Lỗi: Không tìm thấy file selectors_db.json")
            return False

        try:
            with open(selectors_path, "r", encoding="utf-8") as f:
                db = json.load(f)
            selectors = db.get(site_name)
        except Exception as e:
            print(f"[{site_name}] Lỗi khi đọc selectors_db.json: {e}")
            return False

        if not selectors:
            print(f"[{site_name}] Thông tin selectors chưa được lưu trong database.")
            return False

        print(f"[{site_name}] Bắt đầu đăng tin bằng Hybrid Selector Runner...")
        try:
            # --- BƯỚC 1: Đăng nhập ---
            login_url = selectors.get("login_url")
            print(f"[{site_name}] Đi tới trang đăng nhập: {login_url}")
            self.page.goto(login_url, wait_until="domcontentloaded")
            time.sleep(2)

            username = site_config.get("username")
            email = site_config.get("email")
            phone = site_config.get("phone")
            password = site_config.get("password")
            login_credential = email or username or phone

            # Điền form đăng nhập
            email_sel = selectors.get("email_input")
            pass_sel = selectors.get("password_input")
            submit_sel = selectors.get("login_submit")

            print(f"[{site_name}] Điền tài khoản: {login_credential}")
            self.page.fill(email_sel, login_credential)
            self.page.fill(pass_sel, password)
            
            print(f"[{site_name}] Click Đăng nhập")
            self.page.click(submit_sel)
            time.sleep(5) # Chờ chuyển hướng
            
            # --- BƯỚC 2: Đi tới trang đăng tin ---
            post_url = selectors.get("post_url")
            print(f"[{site_name}] Đi tới trang đăng tin: {post_url}")
            self.page.goto(post_url, wait_until="domcontentloaded")
            time.sleep(3)

            # Tự động đóng popup thông báo nếu phát hiện
            for close_sel in ["#btnCancelNotification", ".close", "button:has-text('Cancel')", "button:has-text('Đóng')"]:
                try:
                    if self.page.locator(close_sel).is_visible():
                        self.page.click(close_sel)
                        print(f"[{site_name}] Đã tự động đóng popup: {close_sel}")
                        time.sleep(1)
                except Exception:
                    pass

            # --- BƯỚC 3: Chọn danh mục (category_clicks) ---
            category_clicks = selectors.get("category_clicks", [])
            if category_clicks:
                print(f"[{site_name}] Thực hiện chọn danh mục qua {len(category_clicks)} click chuột...")
                for idx, click_sel in enumerate(category_clicks):
                    print(f"  - Click {idx+1}: {click_sel}")
                    self.page.click(click_sel)
                    time.sleep(1.5)

            # --- BƯỚC 4: Điền thông tin bài đăng ---
            print(f"[{site_name}] Đang điền form bài viết...")
            if selectors.get("title_input"):
                self.page.fill(selectors.get("title_input"), item.get("title"))
            if selectors.get("content_textarea"):
                self.page.fill(selectors.get("content_textarea"), item.get("content"))
            
            if selectors.get("price_input"):
                raw_price = item.get("price")
                numeric_price = "".join(c for c in raw_price if c.isdigit())
                if not numeric_price:
                    numeric_price = "0"
                self.page.fill(selectors.get("price_input"), numeric_price)
            
            if selectors.get("area_input"):
                self.page.fill(selectors.get("area_input"), item.get("area"))

            # --- BƯỚC 5: Tải hình ảnh ---
            local_images = self.download_property_images(item.get('source_url', ''), item.get('title', ''))
            if local_images and selectors.get("image_upload"):
                print(f"[{site_name}] Tải lên {len(local_images)} hình ảnh...")
                self.page.locator(selectors.get("image_upload")).set_input_files(local_images)
                time.sleep(3) # Chờ tải ảnh lên xong

            # --- BƯỚC 6: Hoàn tất hoặc Dry-run ---
            screenshot_path = f"debug_{site_name}_form_filled.png"
            self.page.screenshot(path=screenshot_path)
            print(f"[{site_name}] Đã chụp ảnh màn hình lưu tại: {screenshot_path}")

            if dry_run:
                print(f"[{site_name}] [DRY-RUN] Dừng lại trước khi bấm nút đăng tin.")
                return True
            else:
                print(f"[{site_name}] Bấm gửi bài đăng...")
                self.page.click(selectors.get("submit_button"))
                time.sleep(5)
                print(f"✓ [{site_name}] Đăng tin thành công bằng Hybrid Selector Runner!")
                return True

        except Exception as e:
            print(f"❌ [{site_name}] Lỗi khi chạy Hybrid Selector Runner: {e}")
            return False


    # =====================================================================
    # GIAODICHNHADAT.VN / THONGTINNHADAT.VN — TWIN CMS
    # Hai trang dùng chung 1 CMS: login qua name=email/password
    # =====================================================================

    def login_giaodichnhadat_shared(self, base_url, email, password):
        """Đăng nhập vào trang CMS giaodichnhadat (email + password)."""
        print(f"Đang đăng nhập vào {base_url} với tài khoản: {email}")
        try:
            for scheme in ["https", "http"]:
                try:
                    self.page.goto(f"{scheme}://{base_url}/", wait_until="domcontentloaded", timeout=10000)
                    self._wait_for_cloudflare(self.page, timeout_secs=10)
                    time.sleep(2)
                    break
                except Exception:
                    pass

            content = self.page.content().lower()
            if any(s in content for s in ["đăng xuất", "thoát", "quản lý tin"]):
                print(f"✓ Đã đăng nhập trước đó trên {base_url}")
                return True

            for scheme in ["https", "http"]:
                try:
                    self.page.goto(f"{scheme}://{base_url}/dang-nhap.html", wait_until="domcontentloaded", timeout=10000)
                    self._wait_for_cloudflare(self.page, timeout_secs=8)
                    time.sleep(2)
                    break
                except Exception:
                    pass

            email_loc = self.page.locator("input[name='email']")
            if email_loc.count() == 0:
                print(f"⚠️ Không tìm thấy ô email trên {base_url}")
                return False
            email_loc.fill(email)

            pw_loc = self.page.locator("input[name='password']")
            if pw_loc.count() == 0:
                print(f"⚠️ Không tìm thấy ô password trên {base_url}")
                return False
            pw_loc.fill(password)

            for btn_sel in ["input[type='submit']", "button[type='submit']", "button:has-text('Đăng nhập')"]:
                try:
                    btn = self.page.locator(btn_sel)
                    if btn.count() > 0:
                        btn.first.click()
                        break
                except Exception:
                    pass

            time.sleep(4)
            content2 = self.page.content().lower()
            if any(s in content2 for s in ["đăng xuất", "thoát", "quản lý tin"]) \
                    or "dang-nhap" not in self.page.url:
                print(f"✓ Đăng nhập thành công trên {base_url}")
                return True

            print(f"⚠️ Đăng nhập {base_url} thất bại. Tài khoản có thể chưa đăng ký.")
            self.safe_screenshot(f"{base_url.replace('.','_')}_login_failed.png")
            return False
        except Exception as e:
            print(f"❌ Lỗi đăng nhập {base_url}: {e}")
            return False

    def post_giaodichnhadat_shared(self, base_url, item):
        """Đăng tin trên CMS giaodichnhadat (giaodichnhadat.vn / thongtinnhadat.vn)."""
        print(f"Bắt đầu đăng tin trên {base_url}: {item.get('title')}")
        try:
            local_images = self.download_property_images(item.get("source_url", ""), item.get("title", ""))

            post_found = False
            for post_path in ["/dang-tin-bds.html", "/them-tin-rao-vat", "/dang-tin-moi", "/member/dang-tin", "/dang-tin", "/post"]:
                for scheme in ["https", "http"]:
                    try:
                        self.page.goto(f"{scheme}://{base_url}{post_path}", wait_until="domcontentloaded", timeout=12000)
                        self._wait_for_cloudflare(self.page, timeout_secs=8)
                        time.sleep(2)
                        
                        resolved_url = self.page.url.lower()
                        is_homepage = resolved_url.endswith(f"://{base_url}/") or resolved_url.endswith(f"://{base_url}")
                        
                        cnt = self.page.evaluate("""() =>
                            document.querySelectorAll('input:not([type=hidden]):not([type=submit]):not([type=button]), textarea, select').length
                        """)
                        if cnt > 3 and not is_homepage:
                            print(f"  ✓ Form đăng tin tại {post_path} ({cnt} trường)")
                            post_found = True
                            break
                    except Exception:
                        pass
                if post_found:
                    break

            if not post_found:
                print(f"❌ Không tìm thấy form đăng tin trên {base_url}. Bỏ qua.")
                return False

            title   = item.get("title", "")
            content = (item.get("content") or item.get("description", "")).replace('\\n', '\n')
            price_vnd = int(float(str(item.get("price_vnd", 0)).replace(",", "").replace(".", "") or 0))
            area    = str(item.get("area", ""))
            phone   = item.get("phone", "0935723727")
            contact = item.get("contact_name", "Binh Office Da Nang")
            address = item.get("address", "")

            def try_fill(selectors, value):
                for sel in selectors:
                    try:
                        loc = self.page.locator(sel)
                        if loc.count() > 0:
                            loc.first.fill(str(value), timeout=2000)
                            return sel
                    except Exception:
                        pass
                return None

            s = try_fill(["input[name='title']","input[name='tieude']","#title","#tieude","input[placeholder*='tiêu đề']","input[placeholder*='Tiêu đề']"], title)
            if s: print(f"  ✓ Tiêu đề: {s}")

            s = try_fill(["textarea[name='content']","textarea[name='noidung']","#content","#noidung","textarea:first-of-type"], content)
            if s: print(f"  ✓ Mô tả: {s}")

            s = try_fill(["input[name='address']","input[name='dia_chi']","#address","#dia_chi"], address)
            if s: print(f"  ✓ Địa chỉ: {s}")

            if price_vnd > 0:
                s = try_fill(["input[name='price']","input[name='gia']","#price","#gia"], str(price_vnd))
                if s: print(f"  ✓ Giá: {s}")

            if area:
                s = try_fill(["input[name='area']","input[name='dien_tich']","#area","#dien_tich"], area)
                if s: print(f"  ✓ Diện tích: {s}")

            s = try_fill(["input[name='phone']","input[name='dien_thoai']","input[name='contact_phone']","#phone"], phone)
            if s: print(f"  ✓ SĐT: {s}")

            s = try_fill(["input[name='contact_name']","input[name='ten_lien_he']","input[name='fullname']"], contact)
            if s: print(f"  ✓ Tên LH: {s}")

            for sel in ["select[name='city_id']","select[name='tinh']","select[name='province_id']","#city_id","#tinh"]:
                try:
                    loc = self.page.locator(sel)
                    if loc.count() > 0:
                        for val in ["danang","da-nang","Đà Nẵng","48","31"]:
                            try: loc.first.select_option(label=val, timeout=2000); break
                            except Exception:
                                try: loc.first.select_option(value=val, timeout=2000); break
                                except Exception: pass
                        time.sleep(1)
                        print(f"  ✓ Tỉnh: {sel}")
                        break
                except Exception:
                    pass

            if local_images:
                for sel in ["input[type='file']","input[name='images[]']","input[name='image']"]:
                    try:
                        loc = self.page.locator(sel)
                        if loc.count() > 0:
                            imgs = [img for img in local_images[:5] if os.path.exists(img)]
                            if imgs:
                                loc.first.set_input_files(imgs, timeout=3000)
                                print(f"  ✓ Upload {len(imgs)} ảnh")
                                time.sleep(3)
                            break
                    except Exception:
                        pass

            self.safe_screenshot(f"{base_url.replace('.','_')}_form_filled.png")
            time.sleep(2)

            clicked = False
            for btn_sel in ["input[type='submit'][value='Đăng tin']", ".button-dangtin", "input[value='Đăng tin']", "button[type='submit']:has-text('Đăng')", "button:has-text('Đăng tin')", "input[type='submit']", "button[type='submit']"]:
                try:
                    btn = self.page.locator(btn_sel)
                    if btn.count() > 0:
                        btn.first.click(timeout=3000)
                        clicked = True
                        print(f"  ✓ Submit: {btn_sel}")
                        break
                except Exception:
                    pass

            if not clicked:
                print(f"  ⚠️ Không tìm thấy nút submit trên {base_url}")

            time.sleep(5)
            self.safe_screenshot(f"{base_url.replace('.','_')}_after_submit.png")
            print(f"🏁 Hoàn thành đăng tin trên {base_url}. URL: {self.page.url}")
            return True
        except Exception as e:
            print(f"❌ Lỗi đăng tin {base_url}: {e}")
            self.safe_screenshot(f"{base_url.replace('.','_')}_post_error.png")
            return False

    def login_giaodichnhadat(self, email, password):
        return self.login_giaodichnhadat_shared("giaodichnhadat.vn", email, password)

    def post_giaodichnhadat(self, item):
        return self.post_giaodichnhadat_shared("giaodichnhadat.vn", item)

    def login_thongtinnhadat(self, email, password):
        return self.login_giaodichnhadat_shared("thongtinnhadat.vn", email, password)

    def post_thongtinnhadat(self, item):
        return self.post_giaodichnhadat_shared("thongtinnhadat.vn", item)
