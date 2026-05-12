from google import genai
import json
import re
import requests
import random

class SEOGenerator:
    def __init__(self, api_key, model_name="gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        # Bạn có thể thay API Key Pexels của mình vào đây (Free)
        self.pexels_api_key = "563492ad6f917000010000016026a79895244d5ba81404e38e1201d1" 

    def get_images(self, query, count=3):
        print(f"🔍 Đang tìm ảnh với từ khóa: '{query}'...")
        try:
            url = f"https://api.pexels.com/v1/search?query={query}&per_page={count}&orientation=landscape"
            headers = {"Authorization": self.pexels_api_key}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return [img['src']['large'] for img in data.get('photos', [])]
        except Exception as e:
            print(f"Lỗi tìm ảnh: {e}")
        return []

    def generate_content(self, topic, focus_keyword="", intent="", contact_info=None):
        hotline = contact_info['hotline'] if contact_info else "0935 723 727"
        email = contact_info['email'] if contact_info else "officedanang.vn@gmail.com"
        
        import datetime
        current_year = datetime.datetime.now().year
        
        intent_prompt = f"Mục đích/Định hướng bài viết: {intent}" if intent else ""

        prompt = f"""
        Bạn là một chuyên gia SEO và chuyên gia nội dung hàng đầu. Nhiệm vụ của bạn là viết một bài viết chuyên sâu về chủ đề "{topic}" để đăng lên website Office Danang (officedanang.vn).
        LƯU Ý: Luôn gọi tên thương hiệu là "Office Danang" một cách trang trọng.

        CHỦ ĐỀ: "{topic}"
        TỪ KHÓA CHÍNH (Focus Keyword): "{focus_keyword}"
        {intent_prompt}

        --- YÊU CẦU VỀ NGÔN NGỮ & AI SEARCH ---
        1. NGÔN NGỮ: Sử dụng tiếng Việt chuyên nghiệp, súc tích. HẠN CHẾ tối đa việc lạm dụng thuật ngữ tiếng Anh (VD: thay vì dùng "ROI" hãy dùng "Tỷ suất lợi nhuận", thay vì "Retention" dùng "Giữ chân nhân tài"). Chỉ dùng tiếng Anh khi thực sự cần thiết hoặc là thuật ngữ kỹ thuật phổ biến.
        2. AI SEARCH OPTIMIZATION: Viết nội dung có cấu trúc rõ ràng, dựa trên dữ liệu hoặc phân tích chuyên gia để dễ được các công cụ tìm kiếm AI (như Gemini, Perplexity) đề xuất.

        --- QUY TẮC RANK MATH SEO (MỤC TIÊU 90+ ĐIỂM) ---
        1. TIÊU ĐỀ (Title): Phải chứa "{focus_keyword}" ở đầu. BẮT BUỘC chứa ít nhất một CON SỐ và một TỪ KHÓA MẠNH (Power Word) như: "Sinh Lời", "Bí Quyết", "Tốt Nhất", "Hiệu Quả", "Bền Vững". Độ dài < 60 ký tự.
        2. MỞ ĐẦU: Từ khóa "{focus_keyword}" phải xuất hiện trong 100 chữ đầu tiên.
        3. CẤU TRÚC: Có ít nhất một thẻ H2 và một thẻ H3 chứa "{focus_keyword}".
        4. LIÊN KẾT:
           - 01 liên kết nội bộ (Internal Link) về: https://officedanang.vn/
           - 01 liên kết ngoài (External Link) về nguồn uy tín (Wikipedia, Forbes, hoặc báo chí lớn).
        5. FAQ: Cuối bài phải có ít nhất 05 câu hỏi thường gặp (FAQ) liên quan đến chủ đề, sử dụng cấu trúc heading H3.
        7. HÌNH ẢNH (BẮT BUỘC): 
           - Cung cấp trường "image_search_keyword" trong JSON bằng tiếng Anh (VD: "modern luxury office").
           - Trong nội dung, chèn 2-3 placeholder: [IMAGE_PLACEHOLDER: "English description"].

        --- CẤU TRÚC HTML & STYLE (SIZE CHUẨN THEO MẪU WEBSITE) ---
        1. SCHEMA: Chèn một đoạn <script type="application/ld+json"> chứa Article Schema ở đầu bài viết.
        2. STYLE: Sử dụng inline CSS theo mẫu sau để khớp hoàn toàn với bài viết mẫu:
           - Wrapper: <article style="font-family: 'Montserrat', Arial, sans-serif; line-height: 1.8; color: #334155; max-width: 900px; margin: 0 auto; font-size: 16px; text-align: justify;">
           - H1: <h1 style="color: #092a40; font-size: 30px; font-weight: 700; margin-bottom: 25px; line-height: 1.4;">
           - H2: <h2 style="color: #092a40; font-size: 24px; margin-top: 40px; border-left: 5px solid #28B78D; padding-left: 20px; margin-bottom: 25px; font-weight: 700;">
           - H3: <h3 style="color: #092a40; font-size: 20px; margin-top: 25px; margin-bottom: 20px; font-weight: 700;">
           - Highlight Box: <div style="background-color: #f0fdf4; border-left: 5px solid #28B78D; padding: 25px; border-radius: 8px; margin: 30px 0; font-size: 16px;">
           - Insight Box: <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; padding: 20px; border-radius: 8px; font-style: italic; margin-bottom: 20px; border-left: 4px solid #64748b; font-size: 16px;">
           - CTA Button: <a href="tel:{hotline}" style="color: #ffffff !important; background-color: #28B78D; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: 700; font-size: 17px;">
         4. HÌNH ẢNH (QUAN TRỌNG): 
            - Hãy tự xác định 2-3 vị trí trong bài viết cần có ảnh minh họa để tăng trải nghiệm người dùng. 
            - Tại những vị trí đó, hãy chèn một đoạn text theo cú pháp: [IMAGE_PLACEHOLDER: "mô tả chi tiết ảnh cần tìm bằng tiếng Anh"]. 
            - Ví dụ: [IMAGE_PLACEHOLDER: "modern office lobby with natural light"].
         5. MỤC LỤC: Có một box "Nội dung chính" (Table of Contents) sau đoạn Sapo.

        Trả về JSON:
        {{
            "title": "Tiêu đề chuẩn SEO",
            "slug": "duong-dan-bai-viet",
            "image_search_keyword": "English keyword for featured image",
            "content": "Toàn bộ HTML (bao gồm schema script và inline styles)",
            "meta_description": "Mô tả meta chứa focus keyword và lời kêu gọi hành động",
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
                    
                    # 1. CHÈN ẢNH ĐẠI DIỆN BẮT BUỘC (FEATURED IMAGE)
                    img_query = data.get('image_search_keyword', focus_keyword or topic)
                    main_images = self.get_images(img_query, count=1)
                    if main_images:
                        main_img = main_images[0]
                        main_img_html = f'<div style="margin: 30px 0; text-align: center;"><img src="{main_img}" alt="{focus_keyword}" style="width: 100%; height: auto; border-radius: 12px; box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.15); display: block;"><p style="font-style: italic; color: #64748b; font-size: 14px; margin-top: 10px;">Hình ảnh: {focus_keyword}</p></div>'
                        if "</h1>" in data['content']:
                            data['content'] = data['content'].replace("</h1>", f"</h1>\n{main_img_html}", 1)
                        else:
                            data['content'] = main_img_html + data['content']
                        print(f"✅ Đã chèn ảnh đại diện: {focus_keyword}")
                    else:
                        print(f"⚠️ Không tìm thấy ảnh đại diện cho: {focus_keyword}")

                    # 2. XỬ LÝ CÁC PLACEHOLDER ẢNH TRONG NỘI DUNG
                    # Regex linh hoạt để bắt được: [IMAGE_PLACEHOLDER: "desc"], [IMAGE_PLACEHOLDER: desc], v.v.
                    placeholders = re.findall(r'\[IMAGE_PLACEHOLDER:\s*["\']?(.*?)["\']?\]', data['content'])
                    for desc in placeholders:
                        desc = desc.strip()
                        found_images = self.get_images(desc, count=1)
                        if found_images:
                            img_url = found_images[0]
                            img_tag = f'<div style="margin: 35px 0; text-align: center;"><img src="{img_url}" alt="{focus_keyword} - {desc}" style="width: 100%; height: auto; border-radius: 12px; box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.15); display: block;"><p style="font-style: italic; color: #64748b; font-size: 14px; margin-top: 10px;">Minh họa: {desc}</p></div>'
                            # Thay thế placeholder bằng tag img thực tế
                            pattern = r'\[IMAGE_PLACEHOLDER:\s*["\']?' + re.escape(desc) + r'["\']?\]'
                            data['content'] = re.sub(pattern, img_tag, data['content'])
                            print(f"✅ Đã chèn ảnh nội dung: {desc}")
                        else:
                            # Xóa placeholder nếu không tìm thấy ảnh
                            pattern = r'\[IMAGE_PLACEHOLDER:\s*["\']?' + re.escape(desc) + r'["\']?\]'
                            data['content'] = re.sub(pattern, "", data['content'])
                            print(f"⚠️ Bỏ qua placeholder (không tìm thấy ảnh): {desc}")

                    # Tạo Box ghi chú cho người duyệt bài
                    reviewer_note = f"""
<div style="background-color: #fff3cd; border: 1px solid #ffeeba; color: #856404; padding: 20px; margin-bottom: 30px; border-radius: 8px; font-family: sans-serif;">
    <strong style="font-size: 16px; display: block; margin-bottom: 10px;">⚠️ GHI CHÚ CHO NGƯỜI DUYỆT BÀI (XÓA BOX NÀY KHI ĐĂNG):</strong>
    <ul style="margin: 0; padding-left: 20px;">
        <li><strong>Focus Keyword:</strong> {focus_keyword}</li>
        <li><strong>Slug:</strong> {data.get('slug', '')}</li>
        <li><strong>Meta Description:</strong> {data.get('meta_description', '')}</li>
        <li><strong>Tags:</strong> {data.get('tags', '')}</li>
    </ul>
</div>
"""
                    # Chèn vào đầu nội dung
                    data['content'] = reviewer_note + data['content']
                    
                    # Thêm comment để dễ copy-paste nếu cần
                    data['content'] = f"<!-- BẮT ĐẦU BÀI VIẾT -->\n{data['content']}\n<!-- KẾT THÚC BÀI VIẾT -->"
                    return data
                
            except Exception as e:
                error_msg = str(e)
                if ("503" in error_msg or "429" in error_msg) and i < max_retries - 1:
                    wait_time = 45
                    print(f"⚠️ API bận hoặc hết quota. Đang thử lại sau {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Lỗi: {e}")
                    return None
        return None

if __name__ == "__main__":
    pass
