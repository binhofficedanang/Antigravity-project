import json
import time
from seo_generator import SEOGenerator
from wp_publisher import WPPublisher

import os

def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    config = load_config()
    
    print("--- SEO AUTO POSTER (✨ Powered by Imagen AI) ---")
    generator = SEOGenerator(
        config['gemini']['api_key'],
        model_name=config['gemini']['model']
    )
    publisher = WPPublisher(
        config['wordpress']['url'],
        config['wordpress']['username'],
        config['wordpress']['application_password']
    )
    # 🔗 Kết nối WPPublisher vào Generator để Imagen AI tự upload ảnh lên WordPress
    generator.wp_publisher = publisher
    
    print("--- SEO AUTO POSTER ---")
    print("1. Chạy theo Kế hoạch Nội dung (đọc từ content_plan.json)")
    print("2. Nhập tay từ khóa")
    choice = input("Chọn chế độ (1 hoặc 2): ").strip()
    
    tasks = []
    if choice == '1':
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            plan_path = os.path.join(base_dir, 'content_plan.json')
            if not os.path.exists(plan_path):
                print(f"Lỗi: Không tìm thấy file {plan_path}. Hãy chạy Keyword Research Bot trước.")
                return
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
            for item in plan_data:
                tasks.append({
                    "topic": item.get("topic", ""),
                    "focus_keyword": item.get("focus_keyword", ""),
                    "intent": item.get("intent", ""),
                    "pillar_link": item.get("pillar_link", "")
                })
        except Exception as e:
            print(f"Lỗi khi đọc file kế hoạch: {e}")
            return
    else:
        # Nhập tay như cũ
        keywords_input = input("Nhập các chủ đề bài viết (cách nhau bởi dấu phẩy): ").split(',')
        global_intent = input("Nhập mục đích/định hướng bài viết (để trống nếu không cần): ")
        pillar_input = input("Nhập URL Pillar Link muốn trỏ về (để trống nếu không cần): ").strip()
        for kw in keywords_input:
            kw = kw.strip()
            if kw:
                tasks.append({
                    "topic": kw,
                    "focus_keyword": kw,
                    "intent": global_intent,
                    "pillar_link": pillar_input
                })
                
    if not tasks:
        print("Không có từ khóa nào để chạy.")
        return

    for idx, task in enumerate(tasks):
        topic = task['topic']
        focus_kw = task['focus_keyword']
        current_intent = task['intent']
        pillar_link = task.get('pillar_link', '')
        
        print(f"\n[Bài {idx+1}/{len(tasks)}] Đang tạo nội dung cho: '{topic}'...")
        article_data = generator.generate_content(
            topic=topic, 
            focus_keyword=focus_kw, 
            intent=current_intent, 
            pillar_link=pillar_link,
            contact_info=config['seo_settings']['contact_info']
        )
        
        if article_data:
            print(f"Đang đăng bài: '{article_data['title']}'...")
            status = config['seo_settings'].get('post_status', 'draft')
            
            result = publisher.post_article(
                title=article_data['title'],
                content=article_data['content'],
                status=status,
                slug=article_data.get('slug')
            )
            
            if result:
                print(f"🔗 Link bài viết: {result.get('link')}")
        else:
            print(f"⚠️ Không thể tạo nội dung cho: '{topic}'.")
        
        # Nghỉ 5s giữa các bài viết để hệ thống chạy mượt
        if idx < len(tasks) - 1:
            time.sleep(5)

if __name__ == "__main__":
    main()
