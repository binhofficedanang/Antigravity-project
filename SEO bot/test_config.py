import requests
import base64
import json

def test_wp_connection():
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    wp_config = config['wordpress']
    site_url = wp_config['url']
    username = wp_config['username']
    app_password = wp_config['application_password']
    
    auth_string = f"{username}:{app_password}"
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(auth_string.encode()).decode(),
        'Content-Type': 'application/json'
    }
    
    # Thử lấy thông tin website để check auth
    response = requests.get(site_url.replace('/posts', '/users/me'), headers=headers)
    
    if response.status_code == 200:
        print("✅ Kết nối WordPress THÀNH CÔNG!")
        print(f"Chào {response.json().get('name')}!")
        return True
    else:
        print(f"❌ Kết nối WordPress THẤT BẠI: {response.status_code}")
        print(response.text)
        return False

def test_gemini_connection():
    from google import genai
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    try:
        client = genai.Client(api_key=config['gemini']['api_key'])
        response = client.models.generate_content(
            model=config['gemini']['model'],
            contents="Say 'Gemini OK'"
        )
        if "OK" in response.text:
            print("✅ Kết nối Gemini AI THÀNH CÔNG!")
            return True
    except Exception as e:
        print(f"❌ Kết nối Gemini AI THẤT BẠI: {e}")
    return False

if __name__ == "__main__":
    print("--- KIỂM TRA CẤU HÌNH ---")
    wp_ok = test_wp_connection()
    ai_ok = test_gemini_connection()
    
    if wp_ok and ai_ok:
        print("\n🚀 Mọi thứ đã sẵn sàng! Bạn có thể chạy 'python3 main_seo.py' ngay.")
