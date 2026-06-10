import os
import json
import re
import sys
import subprocess
import requests
from bs4 import BeautifulSoup
from google import genai

class KeywordResearcher:
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, 'config.json')
            
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        api_key = self.config['gemini']['api_key']
        self.model_name = self.config['gemini']['model']
        self.client = genai.Client(api_key=api_key)
        self.output_path = None
        self.script_path = None

    def load_pillar_articles(self):
        if not self.script_path:
            return []
        
        target_dir = os.path.dirname(self.script_path)
        pillar_path = os.path.join(target_dir, 'pillar_articles.json')
        
        if os.path.exists(pillar_path):
            try:
                with open(pillar_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Không thể đọc file pillar: {e}")
        return []

    def fetch_competitor_structure(self, url):
        """Quét và trích xuất CẤU TRÚC (Heading, Meta, Words) từ URL đối thủ."""
        print(f"🔍 Đang 'chụp X-quang' đối thủ tại: {url}...")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Trích xuất dữ liệu
                title = soup.title.string if soup.title else "Không có Title"
                meta_desc = ""
                meta_tag = soup.find('meta', attrs={'name': 'description'})
                if meta_tag:
                    meta_desc = meta_tag.get('content', '')
                
                h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')]
                h2_tags = [h2.get_text(strip=True) for h2 in soup.find_all('h2')]
                h3_tags = [h3.get_text(strip=True) for h3 in soup.find_all('h3')]
                
                # Ước tính số từ
                text_content = soup.get_text(separator=' ', strip=True)
                word_count = len(text_content.split())
                
                structure_data = f"""
TIÊU ĐỀ (Title): {title}
MÔ TẢ (Meta Description): {meta_desc}
SỐ TỪ ƯỚC TÍNH (Word Count): ~{word_count} từ

CẤU TRÚC HEADING:
H1: {', '.join(h1_tags)}

H2 ({len(h2_tags)} thẻ):
"""
                for h2 in h2_tags:
                    structure_data += f"- {h2}\n"
                    
                structure_data += f"\nH3 ({len(h3_tags)} thẻ):\n"
                for h3 in h3_tags[:15]: # Lấy tối đa 15 thẻ H3 để khỏi rối
                    structure_data += f"- {h3}\n"
                
                return structure_data
            else:
                print(f"⚠️ Không thể truy cập URL. Mã lỗi: {response.status_code}")
                return None
        except Exception as e:
            print(f"⚠️ Lỗi khi quét URL đối thủ: {e}")
            return None

    def outrank_competitor(self, competitor_url, seed_topic):
        """Chế độ 2: Nghiên cứu cấu trúc đối thủ và tạo Dàn bài phủ (Outrank Outline)"""
        comp_structure = self.fetch_competitor_structure(competitor_url)
        if not comp_structure:
            print("❌ Thất bại khi phân tích đối thủ. Hãy thử lại với URL khác.")
            return None
            
        pillar_articles = self.load_pillar_articles()
        pillar_context = ""
        if pillar_articles:
            pillar_context = "\nCÁC BÀI VIẾT TRỤ CỘT (PILLAR ARTICLES) HIỆN CÓ ĐỂ TRỎ LINK:\n"
            for p in pillar_articles:
                pillar_context += f"- {p['title']} ({p['url']})\n"

        prompt = f"""
Bạn là một chuyên gia Tình báo SEO và Xây dựng Cấu trúc Nội dung (Content Architect).
Mục tiêu của chúng ta là viết một bài viết về chủ đề "{seed_topic}" nhằm **ĐÁNH BẠI ĐỐI THỦ** trên Google.

Dưới đây là bản "X-quang" cấu trúc bài viết của đối thủ đang Top:
=============================
{comp_structure}
=============================
{pillar_context}

NHIỆM VỤ CỦA BẠN:
1. Đọc và phân tích nhanh cấu trúc đối thủ: Họ mạnh điểm nào? Họ thiếu sót (Content Gap) điểm nào? 
2. Tạo ra một "Báo cáo Tình báo" ngắn gọn gọn (Intelligence Report).
3. Thiết kế một "Dàn bài Kẻ hủy diệt" (Outrank Outline) chi tiết với các thẻ H2, H3 bao trùm toàn bộ ý của đối thủ, NHƯNG bổ sung thêm các phần họ thiếu (ví dụ: So sánh giá, Cập nhật mới nhất 2026, Ý kiến chuyên gia, FAQ...). Dàn bài này phải dài hơn, sâu hơn và hướng tới EEAT.

TRẢ VỀ KẾT QUẢ DƯỚI DẠNG MẢNG JSON HỢP LỆ (Chỉ 1 object duy nhất trong mảng):
[
    {{
        "intelligence_report": "Tóm tắt 3-4 câu về điểm yếu của đối thủ và chiến thuật để thắng họ.",
        "topic": "Tiêu đề bài viết mới (Hấp dẫn hơn, chứa số và từ khóa mạnh)",
        "focus_keyword": "Từ khóa chính ngắn gọn",
        "intent": "DÀN BÀI BẮT BUỘC (Outrank Outline): Liệt kê chi tiết các thẻ H2, H3 cần viết dựa trên phân tích ở trên. (Dữ liệu này sẽ được truyền trực tiếp cho bot viết bài)",
        "pillar_link": "URL bài viết Pillar liên quan nhất (hoặc để trống)"
    }}
]
"""
        import time
        for i in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                
                json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                if json_match:
                    plan_data = json.loads(json_match.group())
                    item = plan_data[0]
                    
                    print("\n" + "="*40)
                    print("🕵️  BÁO CÁO TÌNH BÁO (INTELLIGENCE REPORT)")
                    print("="*40)
                    print(item.get("intelligence_report", "Không có báo cáo."))
                    print("-" * 40)
                    print(f"🎯 TIÊU ĐỀ ĐỀ XUẤT: {item.get('topic')}")
                    print(f"🔑 TỪ KHÓA CHÍNH: {item.get('focus_keyword')}")
                    print(f"🔗 PILLAR LINK: {item.get('pillar_link')}")
                    print(f"📋 DÀN BÀI VƯỢT TRỘI:\n{item.get('intent')}")
                    print("="*40)
                    
                    confirm = input("\nBạn có muốn LƯU kế hoạch 'Đánh bại đối thủ' này không? (y/n): ").strip().lower()
                    if confirm == 'y':
                        if self.output_path:
                            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
                            # Chuẩn hóa lại format để phù hợp với main_seo.py
                            out_plan = [{
                                "topic": item.get("topic"),
                                "focus_keyword": item.get("focus_keyword"),
                                "intent": f"DÀN BÀI BẮT BUỘC:\n{item.get('intent')}",
                                "pillar_link": item.get("pillar_link")
                            }]
                            with open(self.output_path, 'w', encoding='utf-8') as f:
                                json.dump(out_plan, f, ensure_ascii=False, indent=4)
                            print(f"💾 Đã lưu Kế hoạch Nội dung vào: {self.output_path}")
                            return out_plan
                    return None
                else:
                    print("❌ Lỗi định dạng JSON từ AI.")
            except Exception as e:
                print(f"⚠️ Lỗi API: {e}")
                time.sleep(5)
        return None

    def generate_plan(self, seed_topic, context="", num_keywords=None):
        """Chế độ 1: Nghiên cứu từ khóa thông thường (Cluster)"""
        num_keywords = num_keywords or self.config['research_settings'].get('default_num_keywords', 10)
        pillar_articles = self.load_pillar_articles()
        pillar_context = ""
        if pillar_articles:
            pillar_context = "\nCÁC BÀI VIẾT TRỤ CỘT (PILLAR ARTICLES) HIỆN CÓ:\n"
            for p in pillar_articles:
                pillar_context += f"- {p['title']} ({p['url']})\n"
        
        context_prompt = f"\nBỐI CẢNH/MÔ TẢ CHI TIẾT TỪ NGƯỜI DÙNG: {context}" if context else ""
        
        print(f"\n[AI Search/AEO] Đang phân tích không gian mạng cho chủ đề: '{seed_topic}'...")
        prompt = f"""
        Bạn là chuyên gia SEO và AEO. Nhiệm vụ của bạn là nghiên cứu Content Plan cho chủ đề cốt lõi: "{seed_topic}".
        {context_prompt}
        {pillar_context}

        MỤC TIÊU: Tìm ra {num_keywords} chủ đề vệ tinh (cluster content) có thể dẫn dắt người đọc về các BÀI VIẾT TRỤ CỘT đã liệt kê ở trên.
        
        TRẢ VỀ KẾT QUẢ DƯỚI DẠNG MẢNG JSON HỢP LỆ:
        [
            {{
                "topic": "Tiêu đề bài viết đầy đủ",
                "focus_keyword": "Từ khóa chính ngắn gọn",
                "intent": "Mô tả chi tiết mục đích tìm kiếm.",
                "pillar_link": "URL của bài viết Pillar liên quan nhất (hoặc để trống)"
            }}
        ]
        """
        import time
        max_retries = 3
        for i in range(max_retries):
            try:
                response = self.client.models.generate_content(model=self.model_name, contents=prompt)
                json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                if json_match:
                    plan_data = json.loads(json_match.group())
                    print(f"\n✅ Đã tìm thấy {len(plan_data)} từ khóa tiềm năng:")
                    for idx, item in enumerate(plan_data):
                        print(f"  [{idx + 1}] TIÊU ĐỀ: {item.get('topic')} (Keyword: {item.get('focus_keyword')})")
                    
                    choice = input("\nNhập các số thứ tự bạn muốn CHỌN (Ví dụ: 1,3). Nhập 'all' để chọn tất cả, '0' để HỦY: ").strip().lower()
                    
                    final_plan = []
                    if choice == '0':
                        return None
                    elif choice == 'all' or not choice:
                        final_plan = plan_data
                    else:
                        selected_indices = [int(p.strip())-1 for p in choice.split(',') if p.strip().isdigit()]
                        final_plan = [plan_data[i] for i in selected_indices if 0 <= i < len(plan_data)]
                    
                    if final_plan and self.output_path:
                        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
                        with open(self.output_path, 'w', encoding='utf-8') as f:
                            json.dump(final_plan, f, ensure_ascii=False, indent=4)
                        print(f"💾 Đã lưu {len(final_plan)} Kế hoạch vào: {self.output_path}")
                        return final_plan
                    return None
            except Exception as e:
                print(f"⚠️ Lỗi API: {e}")
                time.sleep(5)
        return None

def main():
    print("========================================")
    print("🤖 AI KEYWORD RESEARCH & OUTRANK BOT 🤖")
    print("========================================")
    
    researcher = KeywordResearcher()
    
    print("\n--- BƯỚC 1: CHỌN ĐÍCH ĐẾN (TARGET SITE) ---")
    targets = researcher.config['research_settings'].get('targets', {})
    for tid, target in targets.items():
        print(f"{tid}. {target['name']}")
    
    t_choice = input("Chọn mục tiêu (1, 2...): ").strip()
    if t_choice in targets:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        researcher.output_path = os.path.abspath(os.path.join(base_dir, targets[t_choice]['output_path']))
        researcher.script_path = os.path.abspath(os.path.join(base_dir, targets[t_choice]['script_path']))
        print(f"🎯 Đã chọn mục tiêu: {targets[t_choice]['name']}")
    else:
        print("Lựa chọn không hợp lệ.")
        return

    print("\n--- BƯỚC 2: CHỌN CHẾ ĐỘ HOẠT ĐỘNG ---")
    print("1. Nghiên cứu & Lập kế hoạch nội dung bình thường (Cluster / Khám phá từ khóa mới)")
    print("2. Competitor Outranker (Phân tích cấu trúc 1 link đối thủ & Viết bài đè Top)")
    mode = input("Chọn chế độ (1 hoặc 2): ").strip()

    result = None
    if mode == '2':
        competitor_url = input("\nNhập URL bài viết đối thủ đang đứng Top: ").strip()
        seed_topic = input("Nhập Keyword/Chủ đề bạn muốn SEO cho bài này: ").strip()
        if competitor_url and seed_topic:
            result = researcher.outrank_competitor(competitor_url, seed_topic)
    else:
        seed_topic = input("\nNhập chủ đề cần nghiên cứu (VD: Đất nền Đà Nẵng): ").strip()
        context = input("Nhập bối cảnh/mô tả sâu hơn (Nhấn Enter để bỏ qua): ").strip()
        num_input = input(f"Số lượng từ khóa cần tạo (Enter để dùng mặc định): ").strip()
        num_keywords = int(num_input) if num_input.isdigit() else None
        if seed_topic:
            result = researcher.generate_plan(seed_topic, context, num_keywords)
    
    if result and researcher.script_path:
        print("\n" + "="*40)
        confirm = input("Bạn có muốn CHẠY LUÔN Bot viết bài (seo_generator) không? (y/n): ").strip().lower()
        if confirm == 'y':
            print(f"🚀 Đang khởi động Bot viết bài...")
            subprocess.run([sys.executable, researcher.script_path], check=True)
        else:
            print("👋 Đã xong! Dữ liệu đã lưu vào content_plan.json.")

if __name__ == "__main__":
    main()
