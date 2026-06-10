#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
E-COMMERCE REAL ESTATE CRAWLER & SPIN MACHINE FOR OFFICEDANANG.VN
Tự động cào toàn bộ toà nhà và xào diện tích trống thành hàng trăm tin đăng khác nhau.
"""

import os
import re
import csv
import sys
import time
import argparse
import requests
from bs4 import BeautifulSoup

def convert_price_to_vnd_display(price_str, area_num):
    import re
    price_str = str(price_str).strip().lower()
    usd_rate = 26200
    
    # 1. Thỏa thuận
    if not price_str or "thỏa thuận" in price_str or "thoa thuan" in price_str or "đang cập nhật" in price_str or "liên hệ" in price_str:
        return "Thỏa thuận", "Thỏa thuận", 0
        
    # 2. USD
    if 'usd' in price_str or '$' in price_str or 'đô' in price_str:
        price_match = re.search(r'([\d\.,]+)', price_str)
        if price_match:
            price_val = float(price_match.group(1).replace(',', '.'))
            vnd_m2 = int(price_val * usd_rate)
            total_vnd = int(vnd_m2 * area_num)
            return f"{vnd_m2:,}".replace(',', '.') + " VNĐ/m²/tháng", f"{total_vnd:,}".replace(',', '.') + " VNĐ/tháng", total_vnd
            
    # 3. VNĐ
    price_digits = re.sub(r'[^\d]', '', price_str)
    if price_digits:
        val = int(price_digits)
        if val < 1000000: # Nếu số nhỏ, coi là giá VNĐ/m²/tháng
            vnd_m2 = val
            total_vnd = val * area_num
        else: # Nếu là tổng tiền VNĐ
            total_vnd = val
            vnd_m2 = int(total_vnd / area_num) if area_num > 0 else 0
        return f"{vnd_m2:,}".replace(',', '.') + " VNĐ/m²/tháng", f"{total_vnd:,}".replace(',', '.') + " VNĐ/tháng", total_vnd
        
    return "Thỏa thuận", "Thỏa thuận", 0


def rewrite_listing_with_ollama(building_name, area, price, address, raw_content, scenario="marketing", model="gemma2:2b"):
    """
    Sử dụng Ollama chạy cục bộ để viết lại tiêu đề và mô tả tin đăng dưới dạng text phân tách bằng tiêu đề/nội dung.
    """
    import requests
    
    url = "http://localhost:11434/api/chat"
    
    system_prompt = (
        "Bạn là một chuyên gia marketing bất động sản chuyên nghiệp tại Việt Nam. "
        "Nhiệm vụ của bạn là viết một bài quảng cáo cho thuê văn phòng thật CHI TIẾT, HẤP DẪN. "
        "Bắt buộc viết bài viết hoàn toàn bằng TIẾNG VIỆT tự nhiên, tuyệt đối không dùng tiếng Trung hay bất kỳ ngôn ngữ nào khác."
    )
    
    user_prompt = f"""
Hãy viết lại tin đăng cho thuê văn phòng sau đây theo kịch bản: {scenario}.
Thông tin gốc:
- Tên tòa nhà: {building_name}
- Diện tích: {area} m2
- Giá thuê: {price}
- Địa chỉ: {address}
- Mô tả chi tiết gốc: {raw_content}

Yêu cầu về nội dung:
1. Viết bài bằng tiếng Việt tự nhiên, chuyên nghiệp.
2. Ở phần cuối của NỘI DUNG, hãy tự viết thêm một đoạn văn ngắn khoảng 3-4 câu mô tả chi tiết không gian làm việc thực tế, sự phù hợp cho văn phòng đại diện hoặc công ty công nghệ và kêu gọi liên hệ xem sàn trực tiếp. Tuyệt đối không chép lại các hướng dẫn trong ngoặc vuông dưới đây.

Bạn phải tuân thủ nghiêm ngặt định dạng đầu ra sau đây (viết hoa các nhãn TIÊU ĐỀ: và NỘI DUNG:, dùng dấu gạch đầu dòng và giữ đúng các khoảng cách xuống dòng):

TIÊU ĐỀ:
[Viết tiêu đề tiếng Việt chuẩn, ví dụ: 'Cho thuê văn phòng {area}m2 tại tòa nhà {building_name} Đà Nẵng']

NỘI DUNG:
🏢 CHO THUÊ VĂN PHÒNG TẠI {building_name.upper()}

📍 Địa chỉ: {address}
📐 Diện tích: {area} m2
💵 Giá thuê: {price}

✨ ƯU ĐIỂM & TIỆN ÍCH NỔI BẬT:
- Sàn văn phòng vuông vắn, được thiết kế trống suốt, thoáng đãng với ánh sáng tự nhiên tốt.
- Tòa nhà chuyên nghiệp, thang máy tốc độ cao di chuyển nhanh chóng.
- Hầm gửi xe rộng rãi thoải mái cho nhân viên và đối tác, hệ thống an ninh giám sát 24/7.
- Hệ thống phòng cháy chữa cháy (PCCC) đạt tiêu chuẩn an toàn chất lượng cao.
- Có chính sách hỗ trợ thời gian thi công, setup nội thất văn phòng miễn phí cho doanh nghiệp.

💼 [Viết đoạn văn mô tả thực tế của bạn ở đây]
"""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=40)
        if response.status_code == 200:
            res_json = response.json()
            message_content = res_json.get("message", {}).get("content", "")
            
            # Phân tách tiêu đề và nội dung bằng thuật toán trích xuất văn bản linh hoạt
            content_lower = message_content.lower()
            split_keywords = ["nội dung:", "noi dung:", "content:", "===", "nội dung"]
            title = ""
            content = ""
            
            split_found = False
            for kw in split_keywords:
                if kw in content_lower:
                    idx = content_lower.index(kw)
                    title_part = message_content[:idx].strip()
                    content_part = message_content[idx + len(kw):].strip()
                    
                    # Loại bỏ tiền tố tiêu đề và các ký tự markdown như #, *, [, ]
                    title_prefixes = ["tiêu đề:", "tiêu đe:", "tieu de:", "title:"]
                    title = title_part
                    for pref in title_prefixes:
                        if title.lower().startswith(pref):
                            title = title[len(pref):].strip()
                    title = title.replace("#", "").replace("*", "").replace("[", "").replace("]", "").strip()
                    
                    content = content_part.replace("[", "").replace("]", "").strip()
                    split_found = True
                    break
                    
            if not split_found:
                # Nếu không tìm thấy phân tách, dùng dòng đầu tiên làm tiêu đề, các dòng sau làm nội dung
                lines = [line.strip() for line in message_content.split("\n") if line.strip()]
                if lines:
                    title = lines[0]
                    title_prefixes = ["tiêu đề:", "tiêu đe:", "tieu de:", "title:"]
                    for pref in title_prefixes:
                        if title.lower().startswith(pref):
                            title = title[len(pref):].strip()
                    title = title.replace("#", "").replace("*", "").replace("[", "").replace("]", "").strip()
                    content = "\n\n".join(lines[1:])
            
            if title and content:
                # Xóa bỏ triệt để các phần hướng dẫn trong ngoặc vuông [...] nếu model sao chép lại
                import re
                title = re.sub(r'\[.*?\]', '', title, flags=re.DOTALL).replace("\"", "").replace("'", "").strip()
                content = re.sub(r'💼\s*\[.*?\]', '', content, flags=re.DOTALL)
                content = re.sub(r'\[.*?\]', '', content, flags=re.DOTALL).strip()
                
                # Loại bỏ các dòng chứa hướng dẫn hoặc ngoặc vuông nếu còn sót
                content_lines = []
                for line in content.split('\n'):
                    line_lower = line.lower()
                    if any(kw in line_lower for kw in [
                        "viết đoạn văn", "mô tả thực tế", "hướng dẫn", "ngoặc vuông", 
                        "tuyệt đối không", "thay thế hoàn toàn", "viết một đoạn"
                    ]):
                        continue
                    content_lines.append(line)
                content = '\n'.join(content_lines).strip()
                
                return title, content
    except Exception as e:
        print(f"⚠️ [Ollama] Lỗi kết nối hoặc mô hình chưa sẵn sàng: {e}")
        
    return None, None


class OfficeDanangCrawler:
    def __init__(self):
        self.base_url = "https://officedanang.vn/property_type/van-phong-toa-nha/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "vi,en-US;q=0.7,en;q=0.3"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_total_pages(self):
        """Lấy tổng số trang danh mục để quét"""
        try:
            r = self.session.get(self.base_url, timeout=15)
            if r.status_code != 200:
                return 1
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Tìm phân trang
            pagination = soup.select("ul.page-numbers, ul.pagination, div.pagination")
            if not pagination:
                return 5 # Fallback quét tối đa 5 trang
                
            links = pagination[0].select("a.page-numbers, a.page-link")
            pages = []
            for link in links:
                txt = link.get_text().strip()
                if txt.isdigit():
                    pages.append(int(txt))
            return max(pages) if pages else 5
        except Exception as e:
            print(f"⚠️ Không thể đếm số trang, quét mặc định 5 trang. Lỗi: {e}")
            return 5

    def extract_property_links(self, page_num):
        """Lấy danh sách link tòa nhà từ trang danh mục X"""
        url = self.base_url if page_num == 1 else f"{self.base_url}page/{page_num}/"
        print(f"🔍 Đang quét danh sách trang {page_num}: {url}")
        links = []
        try:
            r = self.session.get(url, timeout=15)
            if r.status_code != 200:
                return []
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Tìm tất cả thẻ a có href chứa /property/
            for a in soup.find_all("a", href=True):
                href = a['href']
                if "/property/" in href and not href.endswith("/property/") and "#" not in href:
                    # Rút gọn link sạch
                    clean_href = href.split('?')[0].split('#')[0]
                    if clean_href not in links:
                        links.append(clean_href)
        except Exception as e:
            print(f"  ❌ Lỗi quét trang {page_num}: {e}")
        return links

    def parse_property_details(self, url):
        """Cào chi tiết thông tin của một toà nhà"""
        print(f"  📄 Cào chi tiết: {url}")
        try:
            r = self.session.get(url, timeout=15)
            if r.status_code != 200:
                return None
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # 1. Tiêu đề (Lấy từ thẻ title của trang để đảm bảo 100% không bị rỗng)
            title = ""
            title_tag = soup.title
            if title_tag:
                title = title_tag.get_text().strip()
                # Tách phần đuôi - Office Danang hoặc các chữ thừa
                title = re.split(r'\s*[\-\|]\s*', title)[0].strip()
            
            if not title:
                title_el = soup.select_one("h1.entry-title, h1.ere-property-title, h1")
                if title_el:
                    title = title_el.get_text().strip()
            
            title = re.sub(r'\s+', ' ', title)
            
            # 2. Địa chỉ chi tiết
            address = ""
            page_text = soup.get_text()
            
            # Tìm link bản đồ để lấy địa chỉ chính xác nhất
            for a in soup.find_all("a", href=True):
                href = a['href']
                if "maps.google" in href or "google.com/maps" in href:
                    txt = a.get_text().strip()
                    if txt and "bản đồ" not in txt.lower() and "google maps" not in txt.lower():
                        address = txt
                        break
            
            if not address:
                addr_el = soup.select_one(".property-address, .address, [class*='address']")
                if addr_el:
                    address = addr_el.get_text().strip()
                else:
                    addr_match = re.search(r'địa chỉ:\s*([^\n]+)', page_text, re.IGNORECASE)
                    if addr_match:
                        address = addr_match.group(1).strip()
            
            if not address:
                address = "Đà Nẵng, Việt Nam"
                
            address = re.sub(r'\s+', ' ', address)

            # 3. Phân tích Quận/Huyện tự động dựa trên địa chỉ (Tránh bị trùng lặp Hải Châu ở chân trang)
            district = "Hải Châu" # Mặc định
            addr_lower = address.lower()
            
            # Map quận từ địa chỉ thực tế
            if "thanh khê" in addr_lower or "thanh khe" in addr_lower or "điện biên phủ" in addr_lower or "lê duẩn" in addr_lower:
                district = "Thanh Khê"
            elif "cẩm lệ" in addr_lower or "cam le" in addr_lower or "xô viết nghệ tĩnh" in addr_lower:
                # Lưu ý: Xô Viết Nghệ Tĩnh thuộc Cẩm Lệ hoặc Hải Châu, ta kiểm tra thêm số nhà hoặc mặc định
                district = "Cẩm Lệ"
                if "06 xô viết nghệ tĩnh" in addr_lower or "hoà cường" in addr_lower:
                    district = "Hải Châu"
            elif "sơn trà" in addr_lower or "son tra" in addr_lower:
                district = "Sơn Trà"
            elif "liên chiểu" in addr_lower or "lien chieu" in addr_lower:
                district = "Liên Chiểu"
            elif "ngũ hành sơn" in addr_lower or "ngu hanh son" in addr_lower:
                district = "Ngũ Hành Sơn"
            else:
                # Quét theo phường/địa danh phổ biến
                for w in ["hoà cường", "hòa cường", "bình thuận", "hải châu", "thuận phước", "thạch thang", "thanh bình", "phước ninh", "nam dương", "hoà thuận", "hòa thuận"]:
                    if w in addr_lower:
                        district = "Hải Châu"
                        break
                for w in ["hoà xuân", "hòa xuân", "khuê trung", "hoà thọ", "hòa thọ", "hoà phát", "hòa phát", "hoà an", "hòa an"]:
                    if w in addr_lower:
                        district = "Cẩm Lệ"
                        break
                for w in ["an hải", "an hai", "phước mỹ", "phuoc my", "thọ quang", "nại hiên", "mân thái"]:
                    if w in addr_lower:
                        district = "Sơn Trà"
                        break
                for w in ["chính gián", "thạc gián", "an khê", "hòa khê", "hoà khê", "tam thuận", "tân chính", "vĩnh trung", "xuân hà"]:
                    if w in addr_lower:
                        district = "Thanh Khê"
                        break

            # 3. Diện tích trống & Diện tích trống nhỏ khác (Để xào bài)
            area_str = "100"
            area_el = soup.select_one(".property-area, .area, [class*='area']")
            if area_el:
                area_str = area_el.get_text().strip()
            else:
                area_match = re.search(r'diện tích trống:\s*([^\n]+)', page_text, re.IGNORECASE)
                if area_match:
                    area_str = area_match.group(1).strip()
            
            # Tìm danh sách diện tích nhỏ khác (để tách bài đăng)
            # ví dụ: "100 - 250 - 350 - 650 m2" hoặc "100, 150, 200"
            split_sizes = []
            
            # Quét trong toàn bộ text trang để tìm các chuỗi dạng diện tích chia nhỏ
            split_patterns = [
                r'(?:chia nhỏ|diện tích trống nhỏ khác|diện tích cho thuê|diện tích|trống)\s*[:\-]?\s*([\d\s\-\,\/]+)\s*m2',
                r'([\d\s\-]+)\s*m2\s*\((?:có thể chia nhỏ|diện tích trống nhỏ khác)',
                r'(\d+)\s*-\s*(\d+)\s*-\s*(\d+)',
            ]
            
            for pat in split_patterns:
                matches = re.findall(pat, page_text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        nums = list(match)
                    else:
                        nums = re.split(r'[\-\,\/\s]+', match)
                    for n in nums:
                        n_clean = re.sub(r'[^\d]', '', n)
                        if n_clean and 20 <= int(n_clean) <= 5000:
                            val = int(n_clean)
                            if val not in split_sizes:
                                split_sizes.append(val)
                if split_sizes:
                    break
                    
            # Chuẩn hóa diện tích chính dạng số
            main_area_match = re.search(r'(\d+)', area_str)
            main_area = int(main_area_match.group(1)) if main_area_match else 100
            
            if not split_sizes:
                split_sizes = [main_area]
            else:
                # Đảm bảo diện tích chính cũng nằm trong danh sách
                if main_area not in split_sizes:
                    split_sizes.append(main_area)
            
            split_sizes = sorted(list(set(split_sizes)))

            # 4. Giá (USD/m2 hoặc Thỏa thuận)
            price_str = "Thỏa thuận"
            price_el = soup.select_one(".property-price, .price, [class*='price']")
            if price_el:
                price_str = price_el.get_text().strip()
            else:
                price_match = re.search(r'giá thuê:\s*([^\n]+)', page_text, re.IGNORECASE)
                if price_match:
                    price_str = price_match.group(1).strip()
            
            # Chuẩn hóa giá tiền
            price_str = re.sub(r'\s+', ' ', price_str)
            if not price_str or price_str.lower() in ["đang cập nhật", "liên hệ"]:
                price_str = "Thỏa thuận"

            # 5. Nội dung mô tả chi tiết
            paragraphs = []
            desc_container = soup.select_one(".property-description, .entry-content, .content")
            if desc_container:
                for el in desc_container.find_all(["p", "li", "h2", "h3", "h4"]):
                    txt = el.get_text().strip()
                    if txt and len(txt) > 20 and "office danang" not in txt.lower():
                        # Định dạng theo thẻ HTML
                        if el.name in ["h2", "h3", "h4"]:
                            formatted = f"🔹 {txt}"
                        elif el.name == "li":
                            formatted = f"- {txt}"
                        elif ":" in txt and len(txt) < 80:
                            formatted = f"- {txt}"
                        else:
                            formatted = txt
                        paragraphs.append(formatted)
            
            if not paragraphs:
                # Dự phòng lấy text thô xung quanh phần mô tả
                lines = [l.strip() for l in page_text.split('\n') if len(l.strip()) > 30]
                paragraphs = lines[5:15] # Lấy một số dòng ở giữa trang
                
            # Ghép nối các đoạn văn thông minh:
            # - Nếu là các dòng gạch đầu dòng kề nhau thì chỉ dùng 1 dấu xuống dòng (\n)
            # - Nếu là đoạn văn/tiêu đề thông thường thì dùng 2 dấu xuống dòng (\n\n) để thông thoáng
            content = ""
            for i, p in enumerate(paragraphs[:12]):
                if i == 0:
                    content += p
                else:
                    prev_p = paragraphs[i-1]
                    if p.startswith("-") and prev_p.startswith("-"):
                        content += "\n" + p
                    else:
                        content += "\n\n" + p

            return {
                "title": title,
                "address": address,
                "district": district,
                "area": main_area,
                "split_sizes": split_sizes,
                "price": price_str,
                "content": content,
                "source_url": url
            }
        except Exception as e:
            print(f"  ❌ Lỗi cào chi tiết: {e}")
            return None

    def crawl_all(self, max_pages=3):
        """Chạy quét toàn bộ trang web và tổng hợp dữ liệu tòa nhà"""
        total_pages = self.get_total_pages()
        pages_to_crawl = min(max_pages, total_pages)
        print(f"🎯 Bắt đầu quét {pages_to_crawl} trang trên tổng số {total_pages} trang của officedanang.vn...")
        
        all_links = []
        for p in range(1, pages_to_crawl + 1):
            links = self.extract_property_links(p)
            print(f"  => Tìm thấy {len(links)} link toà nhà.")
            for link in links:
                if link not in all_links:
                    all_links.append(link)
            time.sleep(1)
            
        print(f"🎉 Tổng cộng thu thập được {len(all_links)} liên kết tòa nhà duy nhất!")
        
        buildings = []
        for i, url in enumerate(all_links):
            print(f"[{i+1}/{len(all_links)}] Đang xử lý...")
            details = self.parse_property_details(url)
            if details:
                buildings.append(details)
                print(f"  => Thành công: {details['title']} | Giá: {details['price']} | Các diện tích: {details['split_sizes']}")
            time.sleep(1)
            
        return buildings

    def spin_and_generate_listings(self, buildings, scenario="long", use_llm=False, llm_model="gemma2:2b"):
        """Xào diện tích trống thành nhiều tin đăng phong phú khác nhau theo các kịch bản nội dung"""
        listings = []
        print(f"\n🌪️  Bắt đầu máy xào tin đăng (Spin Machine) - Kịch bản: {scenario.upper()}...")
        
        # Tải lịch sử đã đăng thực tế để tránh xào lại tiêu đề trùng lặp cũ và lọc trùng tòa nhà
        import json
        posted_history = []
        posted_urls = set()
        posted_titles = set()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        history_path = os.path.join(base_dir, "posted_history.json")
        if os.path.exists(history_path):
            try:
                with open(history_path, "r", encoding="utf-8") as f:
                    posted_history = json.load(f)
            except Exception:
                pass
        
        for hist_item in posted_history:
            if isinstance(hist_item, dict):
                # Chỉ coi là đã đăng nếu không phải "Thất bại"
                if hist_item.get("status") != "Thất bại":
                    url = hist_item.get("source_url", "")
                    if url:
                        posted_urls.add(url.strip().lower())
                    t = hist_item.get("title", "")
                    if t:
                        posted_titles.add(t.strip().lower())
            else:
                posted_titles.add(str(hist_item).strip().lower())
        
        for b in buildings:
            # Bỏ qua nếu tòa nhà này đã được đăng thành công trước đó
            if b['source_url'].strip().lower() in posted_urls:
                print(f"  ⏭️ Bỏ qua tòa nhà đã đăng thành công: {b['title']}")
                continue
                
            # Loại bỏ chữ "Cho thuê văn phòng" hoặc "Tòa nhà" thừa ở đầu tiêu đề gốc
            clean_name = b['title']
            clean_name = re.sub(r'^(?:cho thuê văn phòng|văn phòng cho thuê|toà nhà|tòa nhà)\s+', '', clean_name, flags=re.IGNORECASE)
            # Cắt bỏ phần đuôi địa chỉ dài dòng trong tiêu đề gốc nếu có
            clean_name = clean_name.split('-')[0].split(',')[0].strip()
            
            import random
            
            # Các mẫu tiêu đề phong phú để spin (tránh trùng lặp tiêu đề của cùng tòa nhà khi khác diện tích)
            title_templates = [
                "Cho thuê văn phòng {size}m2 tại {clean_name} - Quận {district}, Đà Nẵng",
                "Văn phòng cho thuê {size}m2 tại tòa nhà {clean_name}, {district}",
                "Cho thuê sàn văn phòng {size}m2 ở {clean_name} - Q. {district}",
                "Cho thuê diện tích văn phòng {size}m2 tại {clean_name} {district}",
                "Cho thuê văn phòng trống {size}m2 cực đẹp ở tòa nhà {clean_name}, {district}",
                "Văn phòng làm việc {size}m2 cho thuê tại {clean_name} Quận {district}"
            ]
            
            # Nếu chọn kịch bản marketing, làm tiêu đề nổi bật hơn
            if scenario == "marketing":
                title_templates = [
                    "🔥 [GIÁ TỐT] Cho thuê văn phòng {size}m2 tòa nhà {clean_name} Q.{district}",
                    "🚀 Cho thuê sàn văn phòng {size}m2 cực đẹp tòa {clean_name} {district}",
                    "💎 Văn phòng cho thuê {size}m2 tòa nhà chuyên nghiệp {clean_name} - {district}",
                    "🌟 Cho thuê văn phòng trống {size}m2 giá tốt tại tòa {clean_name} {district}",
                    "🔥 Sàn văn phòng chuyên nghiệp {size}m2 cho thuê tại {clean_name} {district}"
                ]
            
            for size in b['split_sizes']:
                # Tìm tiêu đề chưa từng đăng bằng cách thử các mẫu template
                available_templates = title_templates.copy()
                title = ""
                while available_templates:
                    temp = random.choice(available_templates)
                    available_templates.remove(temp)
                    candidate_title = temp.format(size=size, clean_name=clean_name, district=b['district'])
                    if candidate_title.strip().lower() not in posted_titles:
                        title = candidate_title
                        break
                
                # Nếu tất cả các mẫu đều đã từng đăng, thêm hậu tố độc bản ngẫu nhiên để làm mới hoàn toàn
                if not title:
                    suffixes = [
                        "giá tốt nhất", "vị trí cực đẹp", "cập nhật mới", "giá ưu đãi", 
                        "hỗ trợ setup", "bàn giao ngay", "sàn trống đẹp", "thiết kế hiện đại",
                        "liên hệ ngay", "giá siêu rẻ", "ưu đãi khủng", "hỗ trợ xem sàn"
                    ]
                    # Thử kết hợp các hậu tố ngẫu nhiên cho đến khi tìm thấy tiêu đề chưa từng trùng lặp
                    for _ in range(50):
                        chosen_suffix = random.choice(suffixes)
                        base_template = random.choice(title_templates)
                        candidate_title = base_template.format(size=size, clean_name=clean_name, district=b['district']) + f" ({chosen_suffix})"
                        if candidate_title.strip().lower() not in posted_titles:
                            title = candidate_title
                            break
                    if not title:
                        # Fallback cuối cùng nếu vẫn trùng: thêm số ngẫu nhiên
                        title = base_template.format(size=size, clean_name=clean_name, district=b['district']) + f" (Mới - LH {random.randint(10, 99)})"
                
                # Quy đổi giá và chuẩn hóa VNĐ
                price_m2_display, price_total_display, total_vnd_numeric = convert_price_to_vnd_display(b['price'], size)
                
                contact_name = "Nguyễn Ngọc Thiên Bình"
                phone = "0935723727"
                footer = f"\n\n📞 Liên hệ xem văn phòng: {phone} ({contact_name})"
                
                # Làm sạch nội dung toà nhà từ đô la sang VNĐ
                def _usd_to_vnd_content(m):
                    try:
                        usd_val = float(m.group(1).replace(',', '.'))
                        vnd_val = int(usd_val * 26200)
                        return f"{vnd_val:,}".replace(',', '.') + " VNĐ"
                    except Exception:
                        return m.group(0).replace('$', '').replace('usd', 'VNĐ').replace('USD', 'VNĐ')
                
                content_detail_clean = re.sub(r'\$([\d]+(?:[\.,]\d+)?)', _usd_to_vnd_content, b['content'])
                content_detail_clean = re.sub(r'([\d]+(?:[\.,]\d+)?)\s*(?:usd|\$|đô|đô-la)', _usd_to_vnd_content, content_detail_clean, flags=re.IGNORECASE)
                
                # PHÂN LOẠI CÁC KỊCH BẢN NỘI DUNG (SCENARIO CONTENT)
                full_content = ""
                
                ai_title, ai_content = None, None
                if use_llm:
                    print(f"🤖 [Ollama] Đang sử dụng AI Qwen2 viết lại tin cho tòa nhà {clean_name} ({size}m2)...")
                    ai_title, ai_content = rewrite_listing_with_ollama(
                        building_name=clean_name,
                        area=size,
                        price=price_total_display,
                        address=b['address'],
                        raw_content=content_detail_clean,
                        scenario=scenario,
                        model=llm_model
                    )
                
                if ai_title and ai_content:
                    title = ai_title
                    full_content = ai_content.strip() + footer
                else:
                    if use_llm:
                        print("🤖 [Ollama] AI rewrite thất bại hoặc chưa bật, tự động fallback về spin template cứng...")
                    if scenario == "short":
                        # Kịch bản 1: Tối giản
                        full_content = (
                            f"🌟 CHO THUÊ VĂN PHÒNG ĐẸP TẠI TÒA NHÀ {clean_name.upper()} 🌟\n\n"
                            f"📍 Địa chỉ: {b['address']}\n"
                            f"📐 Diện tích cho thuê: {size} m2 (trống suốt, ánh sáng tự nhiên tốt)\n"
                            f"💵 Giá thuê: {price_total_display} (Đơn giá: {price_m2_display})\n"
                            f"💼 Phù hợp làm văn phòng đại diện hoặc công ty làm việc."
                        )
                    
                    elif scenario == "medium":
                        # Kịch bản 2: Trung bình (Cơ bản + Tóm tắt ngắn gọn)
                        detail_lines = [l for l in content_detail_clean.split('\n') if l.strip()][:4]
                        summarized_details = "\n".join(detail_lines)
                        full_content = (
                            f"🌟 CHO THUÊ VĂN PHÒNG ĐẸP TẠI TÒA NHÀ {clean_name.upper()} 🌟\n\n"
                            f"📍 Địa chỉ: {b['address']}\n"
                            f"📐 Diện tích cho thuê: {size} m2 (trống suốt, ánh sáng tự nhiên tốt)\n"
                            f"💵 Giá thuê: {price_total_display} (Đơn giá: {price_m2_display})\n"
                            f"💼 Phù hợp cho văn phòng đại diện, quy mô doanh nghiệp vừa và nhỏ.\n\n"
                            f"🔹 TÓM TẮT ĐẶC ĐIỂM NỔI BẬT:\n"
                            f"{summarized_details}"
                        )
                        
                    elif scenario == "basic_lease":
                        # Kịch bản 4: Chào thuê chuyên sâu tài chính
                        full_content = (
                            f"🔥 CƠ HỘI THUÊ VĂN PHÒNG GIÁ TỐT TẠI TÒA NHÀ {clean_name.upper()} 🔥\n\n"
                            f"📍 Vị trí: {b['address']}\n"
                            f"📐 Diện tích sử dụng: {size} m2\n"
                            f"💵 Tổng chi phí thuê: {price_total_display}\n"
                            f"💸 Đơn giá thuê: {price_m2_display}\n\n"
                            f"💼 CÁC THÔNG SỐ BÀN GIAO & VẬN HÀNH:\n"
                            f"- Hiện trạng bàn giao: Sàn trống suốt, đã hoàn thiện trần và chiếu sáng tiêu chuẩn.\n"
                            f"- Mục đích sử dụng: Văn phòng đại diện, trụ sở công ty, trung tâm đào tạo.\n"
                            f"- Thời gian bàn giao: Bàn giao ngay sau khi ký hợp đồng.\n"
                            f"- Hỗ trợ thời gian setup miễn phí: Theo quy mô diện tích thuê."
                        )
                        
                    elif scenario == "marketing":
                        # Kịch bản 5: Quảng cáo / Marketing pitch
                        full_content = (
                            f"🚀 VĂN PHÒNG CHUYÊN NGHIỆP - NÂNG TẦM THƯƠNG HIỆU DOANH NGHIỆP 🚀\n\n"
                            f"Chính chủ cho thuê sàn văn phòng diện tích {size}m2 tại tòa nhà {clean_name.upper()}.\n\n"
                            f"✨ ƯU ĐIỂM VƯỢT TRỘI:\n"
                            f"- Diện tích {size}m2 vuông vắn, dễ thiết kế phân chia phòng ban làm việc.\n"
                            f"- Tòa nhà chuyên nghiệp, có thang máy, điều hòa trung tâm mát mẻ.\n"
                            f"- Hệ thống PCCC đạt chuẩn, hầm để xe rộng rãi, an ninh 24/7.\n"
                            f"- Vị trí cực kỳ đắc địa: {b['address']}, trung tâm kết nối sầm uất.\n\n"
                            f"💰 Giá thuê siêu hấp dẫn: {price_total_display} (Đơn giá: {price_m2_display}).\n"
                            f"🎁 Hỗ trợ tối đa thủ tục pháp lý, ưu đãi cho doanh nghiệp ký hợp đồng dài hạn!"
                        )
                        
                    else: # long (Kịch bản 3: Đầy đủ)
                        content_intro = (
                            f"🌟 CHO THUÊ VĂN PHÒNG ĐẸP TẠI TÒA NHÀ {clean_name.upper()} 🌟\n\n"
                            f"📍 Địa chỉ: {b['address']}\n"
                            f"📐 Diện tích cho thuê: {size} m2 (trống suốt, ánh sáng tự nhiên tốt)\n"
                            f"💵 Giá thuê: {price_total_display} (Đơn giá: {price_m2_display})\n"
                            f"💼 Phù hợp cho văn phòng đại diện, quy mô doanh nghiệp vừa và nhỏ.\n\n"
                            f"🔹 THÔNG TIN CHI TIẾT TÒA NHÀ:\n"
                        )
                        max_chars = 1800
                        available_chars = max_chars - len(footer)
                        
                        full_content = content_intro
                        detail_lines = content_detail_clean.split('\n')
                        for line in detail_lines:
                            if len(full_content) + len(line) + 1 <= available_chars:
                                if full_content.endswith('\n'):
                                    full_content += line
                                else:
                                    full_content += '\n' + line
                            else:
                                break
                    
                    full_content = full_content.strip() + footer
                
                listings.append({
                    "title": title,
                    "category": "Văn phòng",
                    "content": full_content,
                    "price": str(total_vnd_numeric) if total_vnd_numeric > 0 else "Thỏa thuận",
                    "area": size,
                    "address": b['address'],
                    "district": b['district'],
                    "contact_name": contact_name,
                    "phone": phone,
                    "image_path": "",
                    "source_url": b['source_url'],
                    "is_ai": "True" if (ai_title and ai_content) else "False"
                })
                
        print(f"✅ Đã xào xong! Tạo ra tổng cộng {len(listings)} bài đăng từ {len(buildings)} tòa nhà gốc! (Tăng gấp {len(listings)/len(buildings):.1f} lần độ phủ)")
        return listings

def save_to_csv(listings, filepath):
    """Lưu danh sách tin đăng ra tệp CSV"""
    keys = ["title", "category", "content", "price", "area", "address", "district", "contact_name", "phone", "image_path", "source_url", "is_ai"]
    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for item in listings:
                # Encode newlines in content for CSV compatibility
                item_copy = item.copy()
                item_copy['content'] = item_copy['content'].replace('\n', '\\n')
                writer.writerow(item_copy)
        print(f"💾 Đã lưu thành công {len(listings)} tin đăng vào: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Lỗi ghi tệp CSV: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="OfficeDanang Buildings Crawler & Spin Machine")
    parser.add_argument("--pages", type=int, default=2, help="Số trang danh mục cần quét (mặc định: 2)")
    parser.add_argument("--apply", action="store_true", help="Ghi đè trực tiếp vào tệp data.csv để chạy đăng bài ngay")
    parser.add_argument("--scenario", type=str, default="long", choices=["short", "medium", "long", "basic_lease", "marketing"], help="Kịch bản nội dung tin đăng (mặc định: long)")
    parser.add_argument("--llm", action="store_true", help="Sử dụng Local LLM (Ollama) để viết lại nội dung")
    parser.add_argument("--llm-model", type=str, default="qwen2:1.5b", help="Tên model Ollama sử dụng (mặc định: qwen2:1.5b)")
    args = parser.parse_args()

    crawler = OfficeDanangCrawler()
    buildings = crawler.crawl_all(max_pages=args.pages)
    
    if not buildings:
        print("❌ Không tìm thấy toà nhà nào để xử lý!")
        return
        
    listings = crawler.spin_and_generate_listings(
        buildings, 
        scenario=args.scenario,
        use_llm=args.llm,
        llm_model=args.llm_model
    )
    
    output_file = "extracted_listings.csv"
    if args.apply:
        output_file = "data.csv"
        
    save_to_csv(listings, output_file)
    
    print("\n💡 Hướng dẫn chạy:")
    if not args.apply:
        print("1. Kiểm tra lại file 'extracted_listings.csv' vừa tạo.")
        print("2. Chạy lệnh sau để áp dụng trực tiếp và đăng bài:")
        print(f"   python extract_buildings.py --pages 2 --scenario {args.scenario} --apply && python main.py")
    else:
        print("🔥 Đã áp dụng trực tiếp vào 'data.csv'! Bạn có thể chạy bot đăng bài ngay lập tức:")
        print("   python main.py")

if __name__ == "__main__":
    main()
