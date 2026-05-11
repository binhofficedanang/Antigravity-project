import os
import json
import re
from google import genai

class KeywordResearcher:
    def __init__(self, config_path=None):
        if config_path is None:
            # Tự động tìm config.json cùng thư mục với file script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, 'config.json')
            
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        api_key = self.config['gemini']['api_key']
        self.model_name = self.config['gemini']['model']
        self.client = genai.Client(api_key=api_key)
        self.output_path = None # Sẽ được thiết lập khi chọn target

    def generate_plan(self, seed_topic, num_keywords=None):
        num_keywords = num_keywords or self.config['research_settings'].get('default_num_keywords', 10)
        
        print(f"\n[AI Search/AEO] Đang phân tích không gian mạng cho chủ đề: '{seed_topic}'...")
        
        prompt = f"""
        Bạn là chuyên gia SEO và AEO (AI Engine Optimization - Tối ưu hóa công cụ tìm kiếm AI như ChatGPT, Gemini, Copilot).
        Nhiệm vụ của bạn là nghiên cứu và lập ra một Content Plan cho chủ đề cốt lõi: "{seed_topic}".

        MỤC TIÊU: 
        Tìm ra {num_keywords} cụm từ khóa (keywords) và mục đích tìm kiếm (search intents) giúp website ĐƯỢC CÁC CÔNG CỤ AI TRÍCH DẪN (Citation) nhiều nhất.
        Tập trung vào:
        1. Các câu hỏi ngách (FAQs), câu hỏi chuyên sâu mà người dùng thường hỏi AI.
        2. Các truy vấn so sánh, đánh giá, hoặc xin lời khuyên chuyên gia.
        3. Long-tail keywords mang tính chất tìm kiếm thông tin chính xác.

        BẠN PHẢI TRẢ VỀ KẾT QUẢ DƯỚI DẠNG MẢNG JSON HỢP LỆ (chỉ xuất ra JSON, không có code block markdown hay bất kỳ văn bản nào khác).
        Cấu trúc JSON cho mỗi mục phải bao gồm:
        - "topic": Tiêu đề bài viết đầy đủ, hấp dẫn, chuẩn AEO.
        - "focus_keyword": Từ khóa chính ngắn gọn (2-5 từ) để tối ưu Rank Math SEO.
        - "intent": Mô tả chi tiết mục đích tìm kiếm, mong muốn của người dùng và góc nhìn chuyên gia.

        Ví dụ cấu trúc JSON:
        [
            {{
                "topic": "Văn hóa ứng xử tại khu vực Pantry: Những quy tắc ngầm cần biết",
                "focus_keyword": "văn hóa ứng xử văn phòng",
                "intent": "Người dùng muốn tìm hiểu các quy tắc chuyên nghiệp..."
            }}
        ]
        
        Hãy bắt đầu nghiên cứu ngay lập tức.
        """

        import time
        max_retries = 3
        for i in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                
                # Extract JSON from response
                json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                if json_match:
                    plan_data = json.loads(json_match.group())
                    print(f"\n✅ Đã tìm thấy {len(plan_data)} từ khóa tiềm năng. Danh sách:")
                    for idx, item in enumerate(plan_data):
                        print(f"  [{idx + 1}] TIÊU ĐỀ: {item.get('topic')}")
                        print(f"      TỪ KHÓA CHÍNH: {item.get('focus_keyword')}")
                        print(f"      MỤC ĐÍCH: {item.get('intent')}\n")
                    
                    print("\nNhập các số thứ tự bạn muốn CHỌN (Ví dụ: 1,3,4).")
                    print("Nhập 'all' hoặc nhấn Enter để chọn TẤT CẢ.")
                    print("Nhập '0' để HỦY BỎ.")
                    choice = input("Lựa chọn của bạn: ").strip().lower()
                    
                    final_plan = []
                    if choice == '0':
                        print("🚫 Đã hủy bỏ lưu từ khóa.")
                        return None
                    elif choice == 'all' or not choice:
                        final_plan = plan_data
                    else:
                        selected_indices = []
                        for part in choice.split(','):
                            part = part.strip()
                            if part.isdigit():
                                selected_indices.append(int(part) - 1)
                        
                        for i in selected_indices:
                            if 0 <= i < len(plan_data):
                                final_plan.append(plan_data[i])
                                
                        if not final_plan:
                            print("⚠️ Không có từ khóa hợp lệ nào được chọn. Đã hủy bỏ.")
                            return None
                    
                    if not self.output_path:
                        print("❌ Lỗi: Chưa thiết lập đích đến (output path).")
                        return None

                    output_dir = os.path.dirname(self.output_path)
                    if output_dir:
                        os.makedirs(output_dir, exist_ok=True)
                    
                    with open(self.output_path, 'w', encoding='utf-8') as f:
                        json.dump(final_plan, f, ensure_ascii=False, indent=4)
                        
                    print(f"💾 Đã lưu {len(final_plan)} Kế hoạch nội dung vào: {self.output_path}")
                    return final_plan
                else:
                    print("❌ Lỗi: AI không trả về định dạng JSON hợp lệ.")
                    print(f"Phản hồi thô: {response.text}")
                    return None
                    
            except Exception as e:
                error_msg = str(e)
                if ("429" in error_msg or "503" in error_msg) and i < max_retries - 1:
                    wait_time = 45
                    print(f"⚠️ API đang bị giới hạn hoặc quá tải. Đang đợi {wait_time}s rồi thử lại...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Lỗi khi gọi Gemini API: {e}")
                    return None

def main():
    print("========================================")
    print("🤖 AI KEYWORD RESEARCH BOT (AEO/GEO) 🤖")
    print("========================================")
    print("Tối ưu hóa nội dung để được ChatGPT/Gemini trích dẫn.\n")
    
    researcher = KeywordResearcher()
    
    print("--- CHỌN ĐÍCH ĐẾN (TARGET SITE) ---")
    targets = researcher.config['research_settings'].get('targets', {})
    for tid, target in targets.items():
        print(f"{tid}. {target['name']}")
    
    t_choice = input("Chọn mục tiêu (1, 2...): ").strip()
    if t_choice in targets:
        researcher.output_path = targets[t_choice]['output_path']
        print(f"🎯 Đã chọn mục tiêu: {targets[t_choice]['name']}")
    else:
        print("Lựa chọn không hợp lệ. Thoát.")
        return

    seed_topic = input("\nNhập chủ đề cần nghiên cứu (VD: Đất nền Đà Nẵng): ").strip()
    if not seed_topic:
        print("Chủ đề không được để trống!")
        return
        
    num_input = input(f"Số lượng từ khóa cần tạo (Enter để dùng mặc định là {researcher.config['research_settings'].get('default_num_keywords')}): ").strip()
    num_keywords = int(num_input) if num_input.isdigit() else None
    
    researcher.generate_plan(seed_topic, num_keywords)

if __name__ == "__main__":
    main()
