import requests
import base64
import mimetypes
import os

class WPPublisher:
    def __init__(self, site_url, username, app_password):
        self.api_url = site_url.rstrip('/')
        self.auth_string = f"{username}:{app_password}"
        self.headers = {
            'Authorization': 'Basic ' + base64.b64encode(self.auth_string.encode()).decode(),
            'Content-Type': 'application/json'
        }

    def upload_image(self, image_bytes, filename="imagen-ai.jpg", alt_text=""):
        """
        Upload ảnh (dạng bytes) lên WordPress Media Library.
        Trả về URL của ảnh sau khi upload thành công, ngược lại trả về None.
        """
        endpoint = f"{self.api_url}/media"
        media_headers = {
            'Authorization': self.headers['Authorization'],
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'image/jpeg',
        }
        try:
            response = requests.post(
                endpoint,
                headers=media_headers,
                data=image_bytes,
                timeout=60
            )
            if response.status_code == 201:
                media_data = response.json()
                media_url = media_data.get('source_url', '')
                media_id = media_data.get('id', '')
                # Cập nhật alt text nếu có
                if alt_text and media_id:
                    requests.post(
                        f"{self.api_url}/media/{media_id}",
                        headers=self.headers,
                        json={"alt_text": alt_text, "caption": alt_text},
                        timeout=30
                    )
                print(f"✅ Upload ảnh thành công: {media_url}")
                return media_url
            else:
                print(f"⚠️ Upload ảnh thất bại [{response.status_code}]: {response.text[:200]}")
                return None
        except Exception as e:
            print(f"⚠️ Lỗi khi upload ảnh lên WordPress: {e}")
            return None

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
