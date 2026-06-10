import json
import os
import re

class EntityInjector:
    def __init__(self, db_path="shared_entities.json"):
        # Resolve path relative to this script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, db_path)
        
        self.entities = {}
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                self.entities = json.load(f)
        else:
            print(f"⚠️ Không tìm thấy database tại {full_path}")

    def inject_links(self, html_content, current_site_type):
        """
        current_site_type: 'officedanang' hoặc 'propertydanang'
        """
        if not self.entities:
            return html_content

        modified_content = html_content
        
        # Duyệt qua các loại entity (office_buildings, locations, ...)
        for category, items in self.entities.items():
            for item in items:
                # Tìm xem bot đang chạy cho site nào để chọn link của site KIA (Cross-site)
                # Hoặc ưu tiên link nội bộ nếu có.
                target_url = item.get(f'url_{current_site_type}')
                cross_url = item.get('url_propertydanang' if current_site_type == 'officedanang' else 'url_officedanang')
                
                # Ưu tiên Internal Link trước, nếu không có mới dùng Cross-site Link
                link_to_use = target_url if target_url else cross_url
                
                if not link_to_use:
                    continue # Không có link nào để trỏ

                # Tìm và thay thế keyword đầu tiên tìm thấy bằng thẻ <a>
                for kw in item['keywords']:
                    # Tránh thay thế những keyword đã nằm trong thẻ <a> hoặc thuộc tính HTML
                    # Match 1: <a>...</a> block, Match 2: Any <tag>, Match 3: keyword
                    pattern = re.compile(r'(<a\b[^>]*>.*?</a>|<[^>]+>)|(\b' + re.escape(kw) + r'\b)', flags=re.IGNORECASE | re.DOTALL)
                    
                    # Kiểm tra xem keyword có tồn tại không trước khi tốn công sub
                    if re.search(r'\b' + re.escape(kw) + r'\b', modified_content, flags=re.IGNORECASE):
                        replaced = False
                        def repl(m):
                            nonlocal replaced
                            if m.group(1): # Trùng với thẻ HTML hoặc block <a>
                                return m.group(1)
                            if m.group(2): # Trùng với keyword
                                if not replaced:
                                    replaced = True
                                    return f'<a href="{link_to_use}" title="{item["name"]}" style="color: #0056b3; text-decoration: underline; font-weight: 500;" target="_blank">{m.group(2)}</a>'
                                return m.group(2)
                        
                        new_content = pattern.sub(repl, modified_content)
                        if replaced: # Nếu thực sự đã chèn link
                            modified_content = new_content
                            print(f"🔗 Đã tự động chèn liên kết Entity cho từ khóa: '{kw}' trỏ về {link_to_use}")
                            break # Chuyển sang entity tiếp theo sau khi chèn thành công 1 keyword của entity này

        return modified_content

if __name__ == "__main__":
    # Test
    injector = EntityInjector()
    sample_html = "<p>Hôm nay chúng ta sẽ đi thăm Tòa nhà Azura nằm tại quận Sơn Trà nhé.</p>"
    print("Before:", sample_html)
    out = injector.inject_links(sample_html, "officedanang")
    print("After:", out)
