from google import genai
from google.genai import types as genai_types
import json
import re
import requests
import random
import sys
import os
import base64

# Thêm đường dẫn thư mục cha để import entity_injector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from entity_injector import EntityInjector
except ImportError:
    EntityInjector = None

class SEOGenerator:
    def __init__(self, api_key, model_name="gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        # Pexels API Key (dự phòng khi Imagen thất bại)
        self.pexels_api_key = "563492ad6f917000010000016026a79895244d5ba81404e38e1201d1"
        # WordPress publisher (sẽ được set từ bên ngoài nếu cần upload ảnh)
        self.wp_publisher = None

    def get_imagen_image(self, prompt_text, alt_text=""):
        """
        Tạo ảnh bằng Google Imagen AI.
        Trả về URL (nếu wp_publisher có sẵn để upload) hoặc bytes thô.
        Nếu thất bại trả về None để fallback về Pexels.
        """
        print(f"🎨 [Imagen AI] Đang tạo ảnh cho: '{prompt_text[:60]}...' ...")
        try:
            response = self.client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=prompt_text,
                config=genai_types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="16:9",
                    safety_filter_level="block_only_high",
                    person_generation="dont_allow",
                )
            )
            if response.generated_images:
                img_bytes = response.generated_images[0].image.image_bytes
                # Upload lên WordPress nếu có publisher
                if self.wp_publisher and img_bytes:
                    safe_name = re.sub(r'[^a-zA-Z0-9]', '-', prompt_text[:40]).lower()
                    filename = f"imagen-{safe_name}.jpg"
                    wp_url = self.wp_publisher.upload_image(img_bytes, filename=filename, alt_text=alt_text)
                    if wp_url:
                        print(f"✅ [Imagen AI] Ảnh AI đã upload lên WordPress: {wp_url}")
                        return wp_url
                # Fallback: encode base64 để nhúng thẳng vào HTML
                b64 = base64.b64encode(img_bytes).decode('utf-8')
                return f"data:image/jpeg;base64,{b64}"
        except Exception as e:
            print(f"⚠️ [Imagen AI] Thất bại: {e}")
        return None

    def get_images(self, query, count=1, alt_text="", use_imagen=True):
        """
        Lấy ảnh: ưu tiên Imagen AI, fallback về Pexels nếu thất bại.
        """
        # --- Thử Imagen AI trước ---
        if use_imagen:
            imagen_prompt = (
                f"Professional real estate photography, {query}, "
                f"Da Nang Vietnam luxury property, modern architecture, "
                f"bright natural lighting, ultra high quality, 16:9 landscape"
            )
            imagen_url = self.get_imagen_image(imagen_prompt, alt_text=alt_text or query)
            if imagen_url:
                return [imagen_url]

        # --- Fallback: Pexels ---
        print(f"🔄 [Pexels Fallback] Đang tìm ảnh với từ khóa: '{query}'...")
        try:
            url = f"https://api.pexels.com/v1/search?query={query}&per_page={count}&orientation=landscape"
            headers = {"Authorization": self.pexels_api_key}
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return [img['src']['large'] for img in data.get('photos', [])]
        except Exception as e:
            print(f"Lỗi tìm ảnh Pexels: {e}")
        return []

    def generate_content(self, topic, focus_keyword="", intent="", pillar_link="", contact_info=None):
        hotline = contact_info['hotline'] if contact_info else "0935 999 438"
        email = contact_info['email'] if contact_info else "propertydanang.com@gmail.com"
        
        import datetime
        current_year = datetime.datetime.now().year
        
        intent_prompt = f"Mục đích/Định hướng bài viết: {intent}" if intent else ""
        pillar_prompt = f"QUAN TRỌNG: Hãy chèn một liên kết nội bộ tự nhiên trỏ về: {pillar_link} trong nội dung bài viết." if pillar_link else ""

        prompt = f"""
        Bạn là một chuyên gia SEO và Chuyên gia Cố vấn Bất động sản cấp cao với hơn 10 năm kinh nghiệm tại thị trường Đà Nẵng. Mục tiêu là viết một bài viết đạt điểm Rank Math SEO cực cao (80-90+ điểm).
        LƯU Ý QUAN TRỌNG: Hiện tại là năm {current_year}. Đóng vai trò là một chuyên gia chia sẻ góc nhìn thực tế (EEAT).
        Luôn gọi tên thương hiệu là "Property Danang" một cách trang trọng.
        
        CHỦ ĐỀ: "{topic}"
        TỪ KHÓA CHÍNH (Focus Keyword): "{focus_keyword}"
        {intent_prompt}
        {pillar_prompt}

        --- YÊU CẦU VỀ NGÔN NGỮ & TRÁNH AI DETECTION (HUMANIZE) ---
        1. NGÔN NGỮ: Sử dụng tiếng Việt tự nhiên, chuyên nghiệp. Thay đổi linh hoạt độ dài câu văn để tránh bị nhận diện là văn phong AI máy móc.
        2. EEAT: Lồng ghép số liệu giả định hợp lý từ thị trường BĐS Đà Nẵng (Sơn Trà, Ngũ Hành Sơn, Hải Châu...).
        3. AI SEARCH (AEO): Viết nội dung có cấu trúc rõ ràng, dùng list/bullet points để AI Crawler dễ trích xuất.

        --- QUY TẮC RANK MATH SEO BẮT BUỘC ---
        1. TIÊU ĐỀ SEO (Title): Phải chứa "{focus_keyword}" ngay ở đầu. Sử dụng số hoặc tính từ mạnh.
        2. MỞ ĐẦU: Từ khóa "{focus_keyword}" phải xuất hiện trong 100 chữ đầu tiên một cách tự nhiên.
        3. CẤU TRÚC: Ít nhất một thẻ H2 và một thẻ H3 phải chứa từ khóa "{focus_keyword}".
        4. LIÊN KẾT: Chèn 1 internal link về {pillar_link or 'https://propertydanang.com/'} và 1 external link uy tín.
        5. FAQ & SCHEMA: Cuối bài có 05+ FAQ. Nhúng JSON-LD (FAQPage Schema + Article Schema) vào thẻ script.
        6. HÌNH ẢNH: Cung cấp "image_search_keyword" bằng tiếng Anh. Chèn 2-3 [IMAGE_PLACEHOLDER: "English description"].
        
        --- CẤU TRÚC HTML & STYLE CSS BẮT BUỘC ---
        1. BỌC TOÀN BỘ TRONG: <article style="font-family: 'Montserrat', Arial, sans-serif; line-height: 1.8; color: #334155; max-width: 900px; margin: 0 auto; font-size: 16px; text-align: justify;">
        2. H1 (1 lần): <h1 style="color: #1e293b; font-size: 30px; font-weight: 700; margin-bottom: 25px; line-height: 1.4;">
        3. H2: <h2 style="color: #1e293b; font-size: 24px; margin-top: 40px; border-left: 5px solid #de9151; padding-left: 20px; margin-bottom: 25px; font-weight: 700;">
        4. H3: <h3 style="color: #1e293b; font-size: 20px; margin-top: 25px; margin-bottom: 20px; font-weight: 700;">
        5. TOC bắt buộc: <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
        6. Highlight: <div style="background-color: #fef9f3; border-left: 5px solid #de9151; padding: 20px; margin: 30px 0;">
        7. Link màu thương hiệu: <a style="color: #de9151; text-decoration: none;">

        Trả về ĐÚNG MỘT KHỐI JSON (không kèm markdown format):
        {{
            "title": "Tiêu đề chuẩn SEO",
            "slug": "duong-dan-bai-viet",
            "image_search_keyword": "English keyword for featured image",
            "content": "Toàn bộ HTML bao gồm Schema Markup JSON-LD ở cuối",
            "meta_description": "Mô tả meta chứa focus keyword (khoảng 150 ký tự)",
            "tags": "tag1, tag2"
        }}
        """
        
        import time
        max_retries = 3
        for i in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    
                    # 1. KIỂM TRA VÀ CHÈN PILLAR LINK NẾU CHƯA CÓ
                    if pillar_link and pillar_link not in data['content']:
                        cta_link = f'<div style="background-color: #fef9f3; border-left: 5px solid #de9151; padding: 20px; margin: 30px 0;"><strong>Tìm hiểu thêm:</strong> <a href="{pillar_link}" style="color: #de9151; font-weight: bold;">Thông tin chuyên sâu về dự án tại Property Danang</a></div>'
                        if "</h2>" in data['content']:
                            data['content'] = data['content'].replace("</h2>", f"</h2>\n{cta_link}", 1)
                        else:
                            data['content'] += cta_link

                    # 2. CHÈN ẢNH ĐẠI DIỆN BẮT BUỘC (FEATURED IMAGE)
                    img_query = data.get('image_search_keyword', focus_keyword or topic)
                    img_source_label = "📸 Ảnh Stock (Pexels)"
                    main_images = self.get_images(img_query, count=1, alt_text=focus_keyword)
                    if main_images:
                        main_img = main_images[0]
                        if main_img.startswith('data:') or ('propertydanang.com' in main_img) or ('officedanang.vn' in main_img):
                            img_source_label = "🎨 Ảnh AI (Imagen)"
                        main_img_html = f'<div style="margin: 30px 0; text-align: center;"><img src="{main_img}" alt="{focus_keyword}" style="width: 100%; height: auto; border-radius: 12px; box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.15); display: block;"><p style="font-style: italic; color: #64748b; font-size: 14px; margin-top: 10px;">Hình ảnh: {focus_keyword}</p></div>'
                        if "</h1>" in data['content']:
                            data['content'] = data['content'].replace("</h1>", f"</h1>\n{main_img_html}", 1)
                        else:
                            data['content'] = main_img_html + data['content']
                        print(f"✅ Đã chèn ảnh đại diện: {focus_keyword}")

                    # 3. XỬ LÝ CÁC PLACEHOLDER ẢNH TRONG NỘI DUNG
                    placeholders = re.findall(r'\[IMAGE_PLACEHOLDER:\s*["\']?(.*?)["\']?\]', data['content'])
                    for desc in placeholders:
                        desc = desc.strip()
                        found_images = self.get_images(desc, count=1, alt_text=f"{focus_keyword} - {desc}")
                        if found_images:
                            img_url = found_images[0]
                            img_tag = f'<div style="margin: 35px 0; text-align: center;"><img src="{img_url}" alt="{focus_keyword} - {desc}" style="width: 100%; height: auto; border-radius: 12px; box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.15); display: block;"><p style="font-style: italic; color: #64748b; font-size: 14px; margin-top: 10px;">Minh họa: {desc}</p></div>'
                            pattern = r'\[IMAGE_PLACEHOLDER:\s*["\']?' + re.escape(desc) + r'["\']?\]'
                            data['content'] = re.sub(pattern, img_tag, data['content'])

                    # Tạo Box ghi chú cho người duyệt bài
                    reviewer_note = f"""
<div style="background-color: #fff3cd; border: 1px solid #ffeeba; color: #856404; padding: 20px; margin-bottom: 30px; border-radius: 8px; font-family: sans-serif;">
    <strong style="font-size: 16px; display: block; margin-bottom: 10px;">⚠️ GHI CHÚ CHO NGƯỜI DUYỆT BÀI:</strong>
    <ul style="margin: 0; padding-left: 20px;">
        <li><strong>Focus Keyword:</strong> {focus_keyword}</li>
        <li><strong>Pillar Link:</strong> {pillar_link or "N/A"}</li>
        <li><strong>Slug:</strong> {data.get('slug', '')}</li>
        <li><strong>Meta Description:</strong> {data.get('meta_description', '')}</li>
        <li><strong>Nguồn ảnh:</strong> {img_source_label if main_images else '❌ Không có ảnh'}</li>
    </ul>
</div>
"""
                    data['content'] = reviewer_note + data['content']
                    
                    # Tự động chèn Entity Cross-site Links
                    if EntityInjector:
                        injector = EntityInjector()
                        data['content'] = injector.inject_links(data['content'], "propertydanang")

                    data['content'] = f"<!-- BẮT ĐẦU COPY -->\n{data['content']}\n<!-- KẾT THÚC COPY -->"
                    return data
                
            except Exception as e:
                error_msg = str(e)
                if ("503" in error_msg or "429" in error_msg) and i < max_retries - 1:
                    wait_time = 45
                    print(f"⚠️ API bận hoặc hết quota ({error_msg[:30]}...). Đang thử lại sau {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Lỗi: {e}")
                    return None
        return None

if __name__ == "__main__":
    pass
