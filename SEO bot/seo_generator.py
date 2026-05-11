from google import genai
import json
import re

class SEOGenerator:
    def __init__(self, api_key, model_name="gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_content(self, topic, focus_keyword="", intent="", contact_info=None):
        hotline = contact_info['hotline'] if contact_info else "0935 999 438"
        email = contact_info['email'] if contact_info else "propertydanang.com@gmail.com"
        
        import datetime
        current_year = datetime.datetime.now().year
        
        intent_prompt = f"Mục đích/Định hướng bài viết: {intent}" if intent else ""

        prompt = f"""
        Bạn là một chuyên gia SEO hàng đầu, mục tiêu là viết một bài viết đạt điểm Rank Math SEO cực cao (80-90+ điểm).
        LƯU Ý QUAN TRỌNG: Hiện tại là năm {current_year}. Mọi thông tin phải chuẩn xác theo bối cảnh này.
        
        CHỦ ĐỀ: "{topic}"
        TỪ KHÓA CHÍNH (Focus Keyword): "{focus_keyword}"
        {intent_prompt}

        --- QUY TẮC RANK MATH SEO BẮT BUỘC ---
        1. TIÊU ĐỀ SEO (Title): 
           - Phải chứa "{focus_keyword}" ngay ở đầu tiêu đề.
           - Sử dụng số thứ tự (Ví dụ: "Top 5...", "7 cách...") hoặc tính từ mạnh ("Tốt nhất", "Mới nhất {current_year}").
           - Độ dài dưới 60 ký tự.
        2. ĐƯỜNG DẪN (Slug): Tạo slug không dấu, ngăn cách bằng dấu gạch ngang, chứa "{focus_keyword}".
        3. MỞ ĐẦU (Introduction): Từ khóa "{focus_keyword}" phải xuất hiện trong 100 chữ đầu tiên (đoạn sapo).
        4. MẬT ĐỘ TỪ KHÓA: Phân bổ "{focus_keyword}" tự nhiên xuyên suốt bài viết (mật độ khoảng 1%).
        5. CẤU TRÚC HEADING: Ít nhất một thẻ H2 và một thẻ H3 phải chứa từ khóa "{focus_keyword}".
        6. ĐỘ DÀI: Bài viết phải sâu sắc, chuyên môn, tối thiểu 1000 - 1500 chữ.
        7. LIÊN KẾT (Links):
           - Chèn ít nhất 1 liên kết ngoài (External Link) dẫn đến trang uy tín (VD: Wikipedia hoặc các báo lớn).
           - Chèn ít nhất 1 liên kết nội bộ (Internal Link) dẫn về: https://propertydanang.com/
        8. HÌNH ẢNH: Alt text của tất cả các ảnh <img> phải chứa từ khóa "{focus_keyword}".
        9. ĐOẠN VĂN: Mỗi đoạn văn phải ngắn gọn, súc tích (dưới 120 chữ) để dễ đọc trên điện thoại.

        --- BẠN PHẢI SỬ DỤNG CÁC STYLE CSS SAU ---
        1. Wrapper: <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #424242;">
        2. Thẻ <h2>: <h2 style="color: #424242; border-left: 5px solid #de9151; padding-left: 15px; margin-top: 40px; margin-bottom: 20px; font-weight: bold; font-size: 24px;">
        3. Box Expert Insight: <div style="background-color: #fef9f3; border: 1px solid #de9151; border-radius: 6px; padding: 20px; margin: 30px 0;">
           - Bên trong có: <strong style="color: #de9151; display: block; margin-bottom: 10px; text-transform: uppercase; font-size: 14px;">Expert Insight:</strong>
        4. Bảng so sánh (Table):
           - Table: <table style="width: 100%; border-collapse: collapse; margin: 25px 0; box-shadow: 0 0 20px rgba(0,0,0,0.05);">
           - Header (th): <th style="background-color: #424242; color: #fef9f3; text-align: left; padding: 15px; border: 1px solid #555;">
        5. Box CTA Cuối Bài:
           <div style="background-color: #424242; color: #fef9f3; padding: 40px; text-align: center; border-radius: 8px; margin: 50px 0;">
              <h3 style="color: #fef9f3 !important; margin-top: 0; font-size: 22px;">Tiêu đề CTA liên quan "{topic}"</h3>
              <p style="color: #d1d1d1; margin-bottom: 10px;">Liên hệ ngay Hotline {hotline} để nhận tư vấn chuyên sâu.</p>
              <a style="display: inline-block; background-color: #de9151; color: #fff !important; padding: 15px 35px; border-radius: 4px; text-decoration: none; font-weight: bold; text-transform: uppercase;" href="https://propertydanang.com/contact/">Liên Hệ Ngay</a>
           </div>

        Trả về JSON:
        {{
            "title": "Tiêu đề chuẩn SEO",
            "slug": "duong-dan-bai-viet",
            "content": "Toàn bộ HTML chuẩn",
            "meta_description": "Mô tả meta chứa focus keyword (dưới 160 ký tự)",
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
                    data['content'] = f"<!-- BẮT ĐẦU COPY -->\n{data['content']}\n<!-- KẾT THÚC COPY -->"
                    return data
                
            except Exception as e:
                error_msg = str(e)
                if ("503" in error_msg or "429" in error_msg) and i < max_retries - 1:
                    wait_time = 45 # Đợi hẳn 45s vì quota cấp lại khá chậm
                    print(f"⚠️ API bận hoặc hết quota ({error_msg[:30]}...). Đang thử lại sau {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Lỗi: {e}")
                    return None
        return None

if __name__ == "__main__":
    pass
