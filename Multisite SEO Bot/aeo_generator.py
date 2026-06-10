import requests
import json
import os
import re

class AEOGenerator:
    def __init__(self, wp_url, site_name, description):
        self.wp_url = wp_url.rstrip('/') # e.g. https://officedanang.vn/wp-json/wp/v2
        self.site_name = site_name
        self.description = description
        
    def strip_html(self, text):
        """
        Làm sạch HTML: xóa script (bao gồm JSON-LD), style, tag HTML,
        HTML entities và chuẩn hóa khoảng trắng.
        """
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(text, "html.parser")
            # Xóa toàn bộ script (kể cả JSON-LD) và style
            for tag in soup.find_all(["script", "style"]):
                tag.decompose()
            raw = soup.get_text(separator=" ")
        except ImportError:
            # Fallback regex nếu không có bs4
            raw = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
            raw = re.sub(r"<style[\s\S]*?</style>", " ", raw, flags=re.IGNORECASE)
            raw = re.sub(r"<[^>]+>", " ", raw)
        # Giải mã HTML entities (decode 2 lần vì WordPress thường encode 2 lần)
        import html
        raw = html.unescape(html.unescape(raw))
        # Xóa khoảng trắng thừa
        return re.sub(r"\s+", " ", raw).strip()

    def fetch_posts(self, limit=100):
        print(f"📡 Đang lấy dữ liệu từ {self.wp_url}...")
        posts = []
        try:
            response = requests.get(f"{self.wp_url}/posts?per_page={limit}&_fields=id,title,link,content,excerpt")
            if response.status_code == 200:
                posts = response.json()
                print(f"✅ Đã lấy thành công {len(posts)} bài viết.")
            else:
                print(f"⚠️ Lỗi kết nối: {response.status_code}")
        except Exception as e:
            print(f"Lỗi: {e}")
        return posts

    def summarize_content(self, text, use_ai=False, ollama_model="gemma4:e4b"):
        clean_text = self.strip_html(text).strip()
        if not use_ai:
            # Tóm tắt mặc định bằng cách cắt ngắn
            return clean_text[:150] + "..." if len(clean_text) > 150 else clean_text
            
        try:
            print(f"🤖 Đang dùng Ollama ({ollama_model}) tóm tắt nội dung bài viết...")
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": ollama_model,
                    "prompt": (
                        "Hãy đóng vai trò là một chuyên gia tối ưu hóa tìm kiếm AI (GEO/AEO). "
                        "Nhiệm vụ của bạn là viết một đoạn tóm tắt bài viết chuẩn SEO và tối ưu nhất để các mô hình ngôn ngữ lớn (như SearchGPT, Perplexity, Google AI Overviews) dễ dàng trích dẫn làm câu trả lời.\n"
                        "Ràng buộc về định dạng và cấu trúc:\n"
                        "1. Độ dài lý tưởng: Nằm trong khoảng 130 đến 160 từ tiếng Việt.\n"
                        "2. Cấu trúc câu trả lời: Trong 50 từ đầu tiên, hãy đưa ra một định nghĩa trực tiếp, độc lập hoặc câu trả lời trực diện theo dạng 'X là...' hoặc 'Dịch vụ X cung cấp...'. Đoạn văn phải có ý nghĩa trọn vẹn khi đứng một mình mà không cần ngữ cảnh phụ.\n"
                        "3. Giọng văn: Khách quan, thực tế, chứa các số liệu hoặc thông tin cụ thể (nếu có trong văn bản), tránh các từ quảng cáo sáo rỗng hoặc ý kiến chủ quan.\n"
                        "4. Chỉ trả về duy nhất đoạn văn tóm tắt, tuyệt đối không thêm bất kỳ lời dẫn giải, mở bài hay kết bài nào.\n\n"
                        f"Nội dung bài viết để tóm tắt:\n{clean_text[:1000]}"
                    ),
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 220  # ~160 từ tiếng Việt (1 từ ≈ 1.4 token)
                    }
                },
                timeout=120  # gemma4:e4b (9GB) cần tối đa 120s
            )
            if response.status_code == 200:
                summary = response.json().get("response", "").strip()
                if summary:
                    return summary
        except Exception as e:
            print(f"⚠️ Không kết nối được Ollama, sử dụng tóm tắt mặc định: {e}")
            
        return clean_text[:150] + "..." if len(clean_text) > 150 else clean_text

    def generate_files(self, output_dir=".", use_ai=False, ollama_model="gemma4:e4b"):
        posts = self.fetch_posts()
        if not posts:
            return

        if use_ai:
            eta_s = len(posts[:20]) * (8 if "2b" in ollama_model or "1.5b" in ollama_model else 75)
            print(f"⏱️  ETA tóm tắt AI: ~{eta_s//60} phút {eta_s%60} giây ({len(posts[:20])} bài × {'~8s' if eta_s < 200 else '~75s'}/bài với {ollama_model})")

        # 1. Tạo llms.txt (Tóm tắt, cấu trúc sitemap)
        llms_txt = f"# {self.site_name}\n\n> {self.description}\n\n## Nội dung nổi bật\n\n"
        
        for p in posts[:20]: # Chỉ lấy 20 bài mới nhất cho llms.txt để tránh quá dài
            import html as _html
            title = _html.unescape(_html.unescape(p['title']['rendered']))
            link = p['link']
            # Sử dụng nội dung bài viết để sinh tóm tắt chuẩn xác hơn là excerpt WordPress thô
            content_raw = p['content']['rendered']
            excerpt = self.summarize_content(content_raw, use_ai=use_ai, ollama_model=ollama_model)
            llms_txt += f"- [{title}]({link}): {excerpt}\n"

        llms_path = os.path.join(output_dir, "llms.txt")
        os.makedirs(output_dir, exist_ok=True)
        with open(llms_path, "w", encoding="utf-8") as f:
            f.write(llms_txt)
        print(f"💾 Đã tạo {llms_path}")

        # 2. Tạo llms-full.txt (Chứa toàn bộ nội dung text để huấn luyện/RAG)
        llms_full_txt = f"# TOÀN BỘ NỘI DUNG - {self.site_name}\n\n> {self.description}\n\n"
        
        for p in posts:
            title = p['title']['rendered']
            link = p['link']
            content = self.strip_html(p['content']['rendered']).strip()
            llms_full_txt += f"## {title}\nURL: {link}\n\n{content}\n\n---\n\n"

        llms_full_path = os.path.join(output_dir, "llms-full.txt")
        with open(llms_full_path, "w", encoding="utf-8") as f:
            f.write(llms_full_txt)
        print(f"💾 Đã tạo {llms_full_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Search Optimizer (AEO) Generator")
    parser.add_argument("--use-ai", action="store_true", help="Sử dụng local Ollama để sinh tóm tắt chất lượng cao")
    parser.add_argument("--model", type=str, default="gemma4:e4b", help="Mô hình Ollama sử dụng")
    parser.add_argument("--fast", action="store_true",
                        help="Dùng gemma2:2b thay vì gemma4:e4b (~8s/bài thay vì ~75s/bài). Ưu tiên tốc độ.")
    args = parser.parse_args()

    # --fast override model
    if args.fast:
        args.model = "gemma2:2b"
        args.use_ai = True
        print("⚡ Fast mode: dùng gemma2:2b (~8s/bài)")

    print("===============================")
    print("🤖 AI SEARCH OPTIMIZER (AEO)")
    print("===============================")
    
    # Tạo cho Office Danang
    od_gen = AEOGenerator(
        wp_url="https://officedanang.vn/wp-json/wp/v2",
        site_name="Office Danang",
        description="Dịch vụ cho thuê văn phòng chuyên nghiệp tại Đà Nẵng, cung cấp thông tin tòa nhà, giá cả, và tư vấn pháp lý."
    )
    od_gen.generate_files("bot_officedanang", use_ai=args.use_ai, ollama_model=args.model)

    # Tạo cho Property Danang
    pd_gen = AEOGenerator(
        wp_url="https://propertydanang.com/wp-json/wp/v2",
        site_name="Property Danang",
        description="Thông tin các dự án bất động sản, đất nền, căn hộ cao cấp tại Đà Nẵng và miền Trung."
    )
    pd_gen.generate_files("bot_propertydanang", use_ai=args.use_ai, ollama_model=args.model)
    
    print("\n✅ Hoàn tất! Vui lòng upload file llms.txt và llms-full.txt lên thư mục gốc (root directory) của website.")
