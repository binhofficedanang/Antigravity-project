import requests
import base64

class WPPublisher:
    def __init__(self, site_url, username, app_password):
        self.api_url = site_url.rstrip('/')
        self.auth_string = f"{username}:{app_password}"
        self.headers = {
            'Authorization': 'Basic ' + base64.b64encode(self.auth_string.encode()).decode(),
            'Content-Type': 'application/json'
        }

    def post_article(self, title, content, status='draft', categories=None, tags=None, slug=None):
        """
        Đăng bài viết lên WordPress qua REST API.
        """
        endpoint = f"{self.api_url}/posts"
        
        data = {
            'title': title,
            'content': content,
            'status': status,
        }
        
        if slug:
            data['slug'] = slug
        
        # Nếu có tags (chuỗi cách nhau bằng dấu phẩy), chúng ta cần xử lý thêm 
        # (Lưu ý: WP API yêu cầu ID của tag, nhưng để đơn giản ở bước đầu, chúng ta đăng bài trước)
        # TODO: Chuyển đổi tag name thành tag ID
        
        response = requests.post(endpoint, headers=self.headers, json=data)
        
        if response.status_code == 201:
            print(f"✅ Thành công: Bài viết '{title}' đã được đăng (Trạng thái: {status}).")
            return response.json()
        else:
            print(f"❌ Lỗi {response.status_code}: {response.text}")
            return None

if __name__ == "__main__":
    # Test nhanh
    pass
