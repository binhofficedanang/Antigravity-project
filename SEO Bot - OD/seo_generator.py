from google import genai
import json
import re

class SEOGenerator:
    def __init__(self, api_key, model_name="gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_content(self, topic, focus_keyword="", intent="", contact_info=None):
        hotline = contact_info['hotline'] if contact_info else "0935 723 727"
        email = contact_info['email'] if contact_info else "officedanang.vn@gmail.com"
        
        import datetime
        current_year = datetime.datetime.now().year
        
        intent_prompt = f"Mục đích/Định hướng bài viết: {intent}" if intent else ""

        prompt = f"""
        Bạn là một chuyên gia SEO và chuyên gia nội dung hàng đầu. Nhiệm vụ của bạn là viết một bài viết chuyên sâu về chủ đề "{topic}" để đăng lên website officedanang.vn.

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
        6. ĐỘ DÀI: Tối thiểu 1200 - 1500 chữ.

        --- CẤU TRÚC HTML & STYLE (BẮT BUỘC THEO MẪU) ---
        1. SCHEMA: Chèn một đoạn <script type="application/ld+json"> chứa Article Schema ở đầu bài viết.
        2. STYLE: Sử dụng inline CSS theo mẫu sau:
           - Wrapper: <article style="font-family: 'Montserrat', Arial, sans-serif; line-height: 1.8; color: #334155; max-width: 900px; margin: 0 auto;">
           - H1: <h1 style="color: #092a40; font-size: 30px; font-weight: 700; margin-bottom: 25px;">
           - H2: <h2 style="color: #092a40; font-size: 24px; margin-top: 40px; border-left: 5px solid #28B78D; padding-left: 20px; margin-bottom: 25px;">
           - Highlight Box: <div style="background-color: #f0fdf4; border-left: 5px solid #28B78D; padding: 30px; border-radius: 8px; margin: 35px 0;">
           - Insight Box: <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; padding: 25px; border-radius: 8px; font-style: italic; margin-bottom: 20px; border-left: 4px solid #64748b;">
           - CTA Button: <a href="tel:{hotline}" style="color: #ffffff !important; background-color: #28B78D; padding: 18px 36px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: 700;">
        3. MỤC LỤC: Có một box "Nội dung chính" (Table of Contents) sau đoạn Sapo.

        Trả về JSON:
        {{
            "title": "Tiêu đề chuẩn SEO",
            "slug": "duong-dan-bai-viet",
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
