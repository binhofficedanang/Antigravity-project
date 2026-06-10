import os
import re
import time
from .base_adapter import BaseSiteAdapter

class RaoVatNetAdapter(BaseSiteAdapter):
    def login(self, username, password) -> bool:
        email = username
        print(f"Đang đăng nhập raovat.net với email: {email}")
        try:
            self.automation.page.goto("https://raovat.net/dang-nhap", wait_until="domcontentloaded")
            time.sleep(1)
            self.automation.page.fill("input[name='useremail']", email)
            self.automation.page.fill("input[name='password']", password)
            self.automation.page.click("button#buttonLogin")
            time.sleep(3)
            current_url = self.automation.page.url
            if "dang-nhap" not in current_url:
                print(f"=> Đăng nhập raovat.net thành công! URL: {current_url}")
            else:
                user_check = self.automation.page.evaluate(
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

    def post(self, item) -> bool:
        print(f"Bắt đầu đăng tin Raovat: {item.get('title')}")
        try:
            # Tự động tải hình ảnh từ source_url của website hoặc tạo ảnh bìa fallback
            local_images = self.automation.download_property_images(item.get('source_url', ''), item.get('title', ''))

            # --- BƯỚC 1: Chọn danh mục ---
            print("- Bước 1: Chọn danh mục...")
            page_cat = "https://raovat.net/dang-tin-11-Nha-cua-Dat-dai"
            self.automation.page.goto(page_cat, wait_until="domcontentloaded")
            time.sleep(2)

            # Chọn subcategory "Thuê và cho thuê nhà" (subcatid=51) via JS
            self.automation.page.evaluate("""
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
                is_hidden = self.automation.page.evaluate("() => { const btn = document.querySelector('#btnNextStep button'); return btn ? btn.classList.contains('hidden') : true; }")
                if not is_hidden:
                    btn_ready = True
                    break
                time.sleep(1)
                
            self.automation.page.evaluate("""
                () => {
                    const btn = document.querySelector('#btnNextStep button');
                    if (btn) {
                        btn.classList.remove('hidden');
                        btn.click();
                    }
                }
            """)
            time.sleep(5)
            print(f"  => URL step 2: {self.automation.page.url}")

            # Kiểm tra xem có bị chuyển hướng về trang quản lý tin do giới hạn bài đăng
            if "quan-ly" in self.automation.page.url or "Quản lý tin rao vặt" in self.automation.page.title() or "Bạn đang có" in self.automation.page.content():
                print("  ❌ Lỗi: Tài khoản của bạn đã đạt giới hạn số lượng tin đăng cho phép trên raovat.net (hoặc bị chuyển về trang Quản lý tin). Hãy xóa hoặc ẩn bớt các bài đăng cũ trước khi đăng bài mới.")
                return False

            # Chờ form step 2 xuất hiện
            self.automation.page.wait_for_selector("input[name='sitetitle']", timeout=10000)

            # --- BƯỚC 2: Điền form nội dung ---
            print("- Bước 2: Điền tiêu đề...")
            title = item.get('title', '')
            if len(title) > 50:
                title = title[:50].strip()
                print(f"  ⚠️ Cảnh báo: Tiêu đề > 50 ký tự, tự động cắt còn: '{title}'")
            self.automation.page.fill("input[name='sitetitle']", title)

            print("- Chọn loại tin (Thuê - Cho thuê) bằng JS...")
            try:
                self.automation.page.evaluate("""
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
                self.automation.page.evaluate("""
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
                time.sleep(2)

                district_name = item.get('district', '')
                print(f"  => Đang chọn Quận/Huyện: {district_name}")
                
                self.automation.page.evaluate(f"""
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
            price_val = self.automation.parse_price(item.get('price', ''), item.get('area', ''))
            if price_val > 100000:
                self.automation.page.evaluate(f"document.querySelector('input[name=\"siteprice\"]').value = '{price_val}'")
                self.automation.page.evaluate("""
                    () => {
                        const sel = document.querySelector('select[name="sitecurrency"]');
                        if (sel) { sel.value = '1'; sel.dispatchEvent(new Event('change', {bubbles: true})); }
                    }
                """)
                self.automation.page.evaluate("const u = document.querySelector('input[name=\"siteunit\"]'); if(u) u.value = 'tháng';")
                print(f"  => Giá quy đổi: {price_val} VNĐ/tháng")
            else:
                self.automation.page.evaluate("const p = document.querySelector('input[name=\"siteprice\"]'); if(p) p.value = '0';")
                print("  => Giá quy đổi: Thoả thuận (0 VNĐ)")

            print("- Điền nội dung...")
            content = item.get('content', '').replace('\\n', '\n')
            self.automation.page.fill("textarea[name='sitedescription']", content)

            print("- Điền từ khóa...")
            title_words = item.get('title', '').split()[:5]
            tags = ', '.join(title_words)
            self.automation.page.fill("input[name='sitetags']", tags)

            if local_images:
                print("- Tải lên hình ảnh bài viết...")
                try:
                    abs_paths = [os.path.abspath(p) for p in local_images]
                    self.automation.page.set_input_files("input[name='ax_file_input']", abs_paths)
                    time.sleep(2)
                    
                    try:
                        upload_btn = self.automation.page.locator(".ax-upload-all")
                        if upload_btn.count() > 0 and upload_btn.is_visible():
                            upload_btn.click()
                            time.sleep(4)
                            print(f"  => Đã bấm nút Upload All cho {len(local_images)} ảnh")
                        else:
                            self.automation.page.evaluate("if(document.querySelector('.ax-upload-all')) document.querySelector('.ax-upload-all').click();")
                            time.sleep(4)
                            print(f"  => Đã kích hoạt JS Upload All cho {len(local_images)} ảnh")
                    except Exception as ev:
                        print(f"  => Không thể kích hoạt upload all, có thể nó đã tự động tải. Lỗi: {ev}")

                except Exception as e_img:
                    print(f"  ⚠️ Bỏ qua tải ảnh: {e_img}")

            print("- Đóng modal popup nếu có...")
            try:
                self.automation.page.evaluate("""
                    () => {
                        document.querySelectorAll('.modal.in .btn-cancel, .modal.in [data-dismiss="modal"]')
                            .forEach(btn => btn.click());
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
            self.automation.page.evaluate("""
                () => {
                    const btn = document.querySelector('button.btn-success');
                    if (btn) btn.click();
                }
            """)
            time.sleep(6)

            current_url = self.automation.page.url
            page_title = self.automation.page.evaluate("document.title")
            body_text = self.automation.page.evaluate("document.body.innerText")
            print(f"  => URL: {current_url}")
            print(f"  => Title: {page_title}")

            if 'xem' in current_url or 'quan-ly' in current_url:
                print("  ✅ ĐĂNG TIN RAOVAT THÀNH CÔNG!")
                success = True
            elif 'thành công' in body_text.lower():
                print("  ✅ ĐĂNG TIN RAOVAT THÀNH CÔNG (Đã ghi nhận trên hệ thống)!")
                success = True
            else:
                errors = self.automation.page.evaluate("""
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

class ThuvienNhaDatAdapter(BaseSiteAdapter):
    def login(self, username, password) -> bool:
        """Đăng nhập thuviennhadat.vn sử dụng tài khoản thật"""
        print(f"Đang đăng nhập thuviennhadat.vn với tài khoản: {username}")
        try:
            self.automation.page.goto("https://thuviennhadat.vn/Users/Login?returnUrl=%2Fdang-tin", wait_until="domcontentloaded")
            time.sleep(2)
            self.automation.page.fill("input#phone-mail-login-view", username)
            self.automation.page.fill("input#password-login-view", password)
            self.automation.page.click("button#button-submit-login-view")
            
            # Đợi chuyển trang về dang-tin hoặc có cookie session đăng nhập thành công
            self.automation.page.wait_for_url("**/dang-tin**", timeout=15000)
            time.sleep(3)
            
            # Đóng modal chào mừng nếu có
            try:
                if self.automation.page.locator("div.header:has-text('Chào mừng')").is_visible():
                    self.automation.page.click("i.close.icon")
                    time.sleep(1)
            except Exception:
                pass
                
            print("=> Đăng nhập thuviennhadat.vn thành công!")
            return True
        except Exception as e:
            print(f"=> Lỗi đăng nhập thuviennhadat.vn: {e}")
            return False

    def post(self, item) -> bool:
        """Đăng tin lên thuviennhadat.vn theo quy trình 3 bước"""
        import random
        print(f"Bắt đầu đăng tin trên ThuVienNhaDat: {item.get('title')}")
        try:
            # Tự động tải hình ảnh từ source_url của website hoặc tạo ảnh bìa fallback
            local_images = self.automation.download_property_images(item.get('source_url', ''), item.get('title', ''))

            # Luôn đi đến trang dang-tin để đảm bảo form sạch sẽ, tránh ô nhiễm trạng thái giữa các bài đăng
            self.automation.page.goto("https://thuviennhadat.vn/dang-tin", wait_until="domcontentloaded")
            time.sleep(3)

            # Đóng modal chào mừng nếu có
            try:
                if self.automation.page.locator("div.header:has-text('Chào mừng')").is_visible():
                    self.automation.page.click("i.close.icon")
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
                self.automation.page.click(".tag._post-transaction-type._rent")
            else:
                self.automation.page.click(".tag._post-transaction-type._sell")
            time.sleep(1)

            # Mở modal địa chỉ và chọn dropdowns
            print("- Điền địa chỉ...")
            self.automation.page.click("input[name='PostFullAddress']")
            time.sleep(2)

            def select_dropdown(dropdown_selector, search_text):
                self.automation.page.click(dropdown_selector)
                time.sleep(1)
                self.automation.page.fill(f"{dropdown_selector} input.search", search_text)
                time.sleep(2)
                self.automation.page.keyboard.press("Enter")
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
            
            self.automation.page.fill("input[name='AddressName']", street)
            time.sleep(1)
            self.automation.page.click("._btn-submit-location-picking")
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
            self.automation.page.fill("input[name='PostArea']", str(area_val))

            # Nhập mức giá
            price_val = self.automation.parse_price(item.get('price', ''), item.get('area', ''))

            # Với văn phòng cho thuê, ta điền giá dạng VND/m2 (VND/m/Tháng = option value 2)
            if price_val > 100000:
                # Tính giá / m2
                price_per_m2 = int(price_val / area_val)
                self.automation.page.fill("input[name='PostPrice']", str(price_per_m2))
                time.sleep(1)
                # Chọn đơn vị: VND/m2/Tháng (value = 2)
                self.automation.page.click("div.ui.search.dropdown._input-post-price-type")
                time.sleep(1)
                self.automation.page.click("div.ui.search.dropdown._input-post-price-type div.item[data-value='2']")
                time.sleep(1)
                print(f"  => Điền giá quy đổi: {price_per_m2} VND/m²/tháng")
            else:
                # Thỏa thuận
                self.automation.page.click("div.ui.search.dropdown._input-post-price-type")
                time.sleep(1)
                self.automation.page.click("div.ui.search.dropdown._input-post-price-type div.item[data-value='3']")
                time.sleep(1)
                print("  => Điền giá quy đổi: Thỏa thuận")

            # Thêm thông tin liên hệ chính nếu chưa có liên hệ nào hoặc để đảm bảo liên hệ tồn tại
            print("- Thêm liên hệ...")
            try:
                # Click thêm liên hệ thông qua JS evaluate click
                self.automation.page.evaluate('document.querySelector("._btn-contact-adding").click()')
                time.sleep(2)
                # Random tên người liên hệ
                names = ["Bình Office Danang", "Thiên Bình", "Nguyễn Ngọc Thiên Bình", "Mr Bình"]
                selected_name = random.choice(names)
                self.automation.page.fill("input._input-contact-name", selected_name)
                print(f"  => Điền thông tin liên hệ: {selected_name}")
                self.automation.page.fill("input._input-contact-phone", "0935723727")
                self.automation.page.click("._modal-contact-adding .ui.checkbox label")
                time.sleep(1)
                self.automation.page.click("._btn-submit-contact-adding")
                time.sleep(2)
                print("  => Đã thêm/cập nhật thông tin liên hệ thành công")
            except Exception as e_contact:
                print(f"  => Liên hệ chính đã có sẵn hoặc bỏ qua: {e_contact}")

            # Điền tiêu đề & mô tả
            print("- Điền tiêu đề & mô tả...")
            self.automation.page.fill("textarea[name='PostTitle']", item.get('title', ''))
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
            self.automation.page.fill("textarea[name='PostDescription']", content_clean)

            # Nhấn Tiếp tục để sang Bước 2
            print("- Click Tiếp tục sang Bước 2...")
            self.automation.page.click(".next-step-btn")
            time.sleep(5)

            # --- BƯỚC 2: Hình ảnh & video ---
            if local_images:
                print("- Tải lên hình ảnh...")
                try:
                    # Lấy đường dẫn tuyệt đối của tất cả các ảnh cục bộ
                    abs_paths = [os.path.abspath(p) for p in local_images]
                    self.automation.page.set_input_files("input#_input-post-images", abs_paths)
                    time.sleep(6) # Chờ load ảnh preview
                    print(f"  => Đã tải lên {len(abs_paths)} ảnh thành công")
                except Exception as e_upload:
                    print(f"  ⚠️ Lỗi khi tải ảnh: {e_upload}")
            else:
                print("  ⚠️ Không có ảnh cục bộ nào để upload.")

            # Nhấn Tiếp tục để sang Bước 3
            print("- Click Tiếp tục sang Bước 3...")
            self.automation.page.click(".next-step-btn")
            time.sleep(5)

            # --- BƯỚC 3: Cấu hình tin đăng ---
            print("- Chọn gói đăng tin Tiêu chuẩn (Miễn phí)...")
            try:
                self.automation.page.click("div.card.__post-type[data-packagetype='1']")
                time.sleep(2)
            except Exception as e_pack:
                print(f"  => Không chọn được gói Tiêu chuẩn, bỏ qua dùng mặc định: {e_pack}")

            # Chọn thời hạn đăng 30 ngày thay vị mặc định 7 ngày
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
                        if self.automation.page.locator(sel).count() > 0:
                            self.automation.page.click(sel)
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
                            if self.automation.page.locator(sel).count() > 0:
                                self.automation.page.select_option(sel, "30")
                                selected_30 = True
                                print(f"  => Đã chọn 30 ngày qua dropdown: {sel}")
                                time.sleep(1)
                                break
                        except:
                            pass

                # Thử tìm qua JS nếu vẫn chưa chọn được
                if not selected_30:
                    self.automation.page.evaluate("""
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
                self.automation.safe_screenshot("thuviennhadat_step3_debug.png")
                with open("thuviennhadat_step3_debug.html", "w", encoding="utf-8") as f:
                    f.write(self.automation.page.content())
                print("  => Đã lưu ảnh chụp và mã HTML của Bước 3 để phân tích")
            except Exception as e_debug:
                print(f"  ⚠️ Lỗi khi lưu file gỡ lỗi: {e_debug}")

            # Nhấn Tiếp tục để sang bước xác nhận/thanh toán cuối cùng
            print("- Click Tiếp tục sang bước thanh toán/xác nhận...")
            try:
                next_btn = self.automation.page.locator(".next-step-btn")
                if next_btn.count() > 0 and next_btn.is_visible():
                    next_btn.click()
                    print("  => Đã click nút Tiếp tục sang màn xác nhận qua Playwright")
                else:
                    self.automation.page.evaluate("document.querySelector('.next-step-btn').click()")
                    print("  => Đã click nút Tiếp tục sang màn xác nhận qua JavaScript")
                time.sleep(3)
                
                # Kiểm tra và xử lý modal khuyến mãi/popup (nếu có)
                for _ in range(3):
                    promo_btn = self.automation.page.locator(".btn-skiped-promo, .btn-used-promo")
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
                final_btn = self.automation.page.locator(".final-step-btn")
                
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
                    self.automation.page.evaluate("document.querySelector('.final-step-btn').click()")
                    print("  => Đã gửi lệnh click JS cho nút Đăng tin (.final-step-btn)")
                time.sleep(8)
            except Exception as e_click:
                print(f"  ⚠️ Lỗi click Đăng tin, thử click lại qua JS thay thế: {e_click}")
                try:
                    self.automation.page.evaluate("document.querySelector('.final-step-btn').click()")
                    time.sleep(8)
                except Exception as e_alt:
                    print(f"  ⚠️ Thất bại hoàn toàn khi gửi form ở Bước 3: {e_alt}")
                    raise e_click

            # Kiểm tra kết quả
            current_url = self.automation.page.url
            body_text = self.automation.page.evaluate("document.body.innerText")
            print(f"  => URL hiện tại: {current_url}")
            
            success_keywords = ["quan-ly", "thành công", "đã được ghi nhận", "kết quả đăng tin", "mã tin"]
            is_success = "quan-ly" in current_url or any(kw in body_text.lower() for kw in success_keywords)
            
            if is_success:
                print("  ✅ ĐĂNG TIN THUVIENNHADAT THÀNH CÔNG!")
                try:
                    post_id = self.automation.page.locator("#_partial-code-post-compeled").inner_text(timeout=2000).strip()
                    if post_id and post_id != "0":
                        print(f"  => Mã tin đăng: {post_id}")
                except Exception:
                    pass
                return True
            else:
                self.automation.safe_screenshot("thuviennhadat_submit_failed.png")
                print("  ⚠️ Hãy kiểm tra lại trạng thái tin đăng trong trang Quản lý tin. Đã lưu thuviennhadat_submit_failed.png")
                return False
        except Exception as e:
            print(f"=> Lỗi đăng tin thuviennhadat: {e}")
            return False

