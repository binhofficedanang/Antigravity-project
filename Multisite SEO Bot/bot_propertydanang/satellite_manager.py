import json
import time
from seo_generator import SEOGenerator
from wp_publisher import WPPublisher

class SatelliteManager:
    def __init__(self, config_path="config.json", buildings_path="buildings_data.json"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        with open(buildings_path, "r", encoding="utf-8") as f:
            self.buildings = json.load(f)
        
        self.generator = SEOGenerator(
            api_key=self.config["gemini"]["api_key"],
            model_name=self.config["gemini"]["model"]
        )

    def run(self):
        print(f"🚀 Bắt đầu triển khai nội dung cho {len(self.buildings)} tòa nhà vệ tinh...")
        
        for building in self.buildings:
            if building.get("status") != "active":
                continue
                
            print(f"\n--- Đang xử lý tòa nhà: {building['name']} ---")
            
            # Tạo prompt đặc thù cho trang "Tổng quan tòa nhà"
            topic = f"Tổng quan dự án {building['name']} - {building['location']}"
            intent = f"""
            Đây là trang chủ của một website vệ tinh dành riêng cho tòa nhà {building['name']}.
            Nội dung cần tập trung vào:
            1. Vị trí đắc địa: {building['location']}
            2. Các điểm nổi bật: {building['highlights']}
            3. Mục đích chính là thu hút khách hàng quan tâm đến: {building['focus_keyword']}
            4. Cuối bài phải khéo léo dẫn về dịch vụ tư vấn của công ty: {building['consulting_service']}
            Viết theo phong cách chuyên nghiệp, tin cậy của một đơn vị quản lý/tư vấn bất động sản hàng đầu.
            """
            
            # 1. Sinh nội dung từ AI
            print(f"🤖 Đang sinh nội dung SEO cho {building['name']}...")
            article_data = self.generator.generate_content(
                topic=topic,
                focus_keyword=building['focus_keyword'],
                intent=intent,
                contact_info=self.config["seo_settings"]["contact_info"]
            )
            
            if not article_data:
                print(f"❌ Thất bại khi sinh nội dung cho {building['name']}")
                continue

            # 2. Đăng lên WordPress của Subdomain tương ứng
            # Lưu ý: Chúng ta ghi đè URL từ config bằng subdomain_url của tòa nhà
            subdomain_api_url = f"{building['subdomain_url'].rstrip('/')}/wp-json/wp/v2"
            
            print(f"📤 Đang đăng lên hệ thống: {building['subdomain_url']}...")
            publisher = WPPublisher(
                site_url=subdomain_api_url,
                username=self.config["wordpress"]["username"],
                app_password=self.config["wordpress"]["application_password"]
            )
            
            result = publisher.post_article(
                title=article_data['title'],
                content=article_data['content'],
                status=self.config["seo_settings"]["post_status"],
                slug=article_data['slug']
            )
            
            if result:
                print(f"✅ Đã hoàn thành vệ tinh cho: {building['name']}")
            else:
                print(f"⚠️ Không thể đăng bài cho {building['name']}. Hãy kiểm tra lại cấu hình Subdomain.")

            # Nghỉ một chút để tránh spam API
            time.sleep(5)

if __name__ == "__main__":
    manager = SatelliteManager()
    manager.run()
