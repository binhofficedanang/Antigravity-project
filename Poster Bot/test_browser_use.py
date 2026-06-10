import asyncio
import os
import json
import csv
import argparse
from dotenv import load_dotenv

# Nạp các biến môi trường từ file .env nếu có
load_dotenv()

def load_config(filepath="config.json"):
    if not os.path.exists(filepath):
        print(f"❌ Không tìm thấy file cấu hình {filepath}")
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def load_data(filepath="data.csv"):
    data = []
    if not os.path.exists(filepath):
        print(f"❌ Không tìm thấy file dữ liệu {filepath}")
        return data
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def get_property_images(property_title):
    import re
    # Chuẩn hóa tên thư mục giống như WebAutomation làm
    safe_title = re.sub(r'[^\w\-_\. ]', '', property_title).strip().replace(' ', '_')
    download_dir = os.path.abspath(os.path.join("downloads", safe_title))
    
    if os.path.exists(download_dir):
        files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        return files
    return []

async def main():
    parser = argparse.ArgumentParser(description="Browser-Use Poster Test POC")
    parser.add_argument("-s", "--site", type=str, default="raovat.net",
                        help="Trang web muốn thử nghiệm (mặc định: raovat.net)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Chế độ chạy thử không nhấn nút submit cuối cùng")
    parser.add_argument("--headless", action="store_true",
                        help="Chạy ở chế độ ẩn danh (không hiện trình duyệt)")
    parser.add_argument("--llm", type=str, default="gemini", choices=["gemini", "ollama"],
                        help="Chọn LLM để chạy (gemini hoặc ollama)")
    parser.add_argument("--ollama-model", type=str, default="gemma4:e4b",
                        help="Tên mô hình Ollama (mặc định: gemma4:e4b)")
    args = parser.parse_args()

    print("=== BẮT ĐẦU CHẠY THỬ NGHIỆM BROWSER-USE AGENT ===")
    
    # 1. Thiết lập LLM
    if args.llm == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ Cảnh báo: Không tìm thấy biến môi trường GEMINI_API_KEY.")
            config = load_config()
            api_key = config.get("gemini_api_key") or config.get("GEMINI_API_KEY")
            if api_key:
                os.environ["GEMINI_API_KEY"] = api_key
                print("✓ Đã tải GEMINI_API_KEY từ config.json")
            else:
                api_key = input("Nhập GEMINI_API_KEY của bạn: ").strip()
                if not api_key:
                    print("❌ Lỗi: GEMINI_API_KEY là bắt buộc để sử dụng Gemini Model.")
                    return
                os.environ["GEMINI_API_KEY"] = api_key
        
        try:
            from browser_use import ChatGoogle
        except ImportError as e:
            print(f"❌ Lỗi import ChatGoogle: {e}")
            return
            
        llm = ChatGoogle(model="gemini-2.5-flash", api_key=api_key)
        print("✓ Sử dụng mô hình Google Gemini 2.5 Flash")

    elif args.llm == "ollama":
        try:
            from langchain_ollama import ChatOllama
            llm = ChatOllama(
                model=args.ollama_model,
                num_ctx=32000,
                temperature=0.0
            )
            print(f"✓ Sử dụng mô hình Ollama cục bộ: {args.ollama_model}")
        except ImportError:
            try:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    model=args.ollama_model,
                    api_key="ollama",
                    base_url="http://localhost:11434/v1",
                    temperature=0.0
                )
                print(f"✓ Sử dụng mô hình Ollama qua API OpenAI tương thích: {args.ollama_model}")
            except ImportError as e:
                print(f"❌ Thiếu thư viện langchain-ollama hoặc langchain-openai. Hãy chạy: pip install langchain-ollama")
                return

    # 2. Load cấu hình & dữ liệu tin đăng
    config = load_config()
    data = load_data()
    
    if not data:
        print("❌ Dữ liệu trống hoặc không tìm thấy data.csv.")
        return

    # Lấy tài khoản tương ứng với trang được chọn
    site_config = config.get(args.site)
    if not site_config:
        print(f"❌ Không tìm thấy thông tin tài khoản cho trang {args.site} trong config.json")
        return
        
    username = site_config.get("username")
    email = site_config.get("email")
    phone = site_config.get("phone")
    password = site_config.get("password")
    
    if not (username or email or phone) or not password:
        print(f"❌ Tài khoản hoặc mật khẩu trống cho trang {args.site}")
        return

    # Lấy tin đăng đầu tiên để chạy thử
    item = data[0]
    print(f"\n📄 Bài đăng thử nghiệm: {item.get('title')}")
    print(f"📍 Địa chỉ: {item.get('address')}")
    print(f"💵 Giá: {item.get('price')} | Diện tích: {item.get('area')}m²")

    # Lấy đường dẫn hình ảnh cục bộ (nếu có)
    images = get_property_images(item.get('title', ''))
    print(f"🖼️ Hình ảnh cục bộ tìm thấy: {len(images)} ảnh")
    for img in images:
        print(f"  - {os.path.basename(img)}")

    # 3. Import thư viện browser-use
    try:
        from browser_use import Agent, Browser
    except ImportError as e:
        print(f"❌ Thiếu thư viện browser-use. Chi tiết lỗi: {e}")
        return

    # 4. Thiết lập prompt
    login_url = f"https://{args.site}"
    if args.site == "raovat.net":
        login_url = "https://raovat.net/dang-nhap"
    elif args.site == "123nhadatviet.com":
        login_url = "https://123nhadatviet.com/dang-nhap.html"
    elif args.site == "thuviennhadat.vn":
        login_url = "https://thuviennhadat.vn/dang-nhap"
        
    # Mô tả chi tiết hình ảnh để AI tải lên
    image_list_str = "\n".join([f"- {img}" for img in images])
    
    dry_run_instruction = ""
    if args.dry_run:
        dry_run_instruction = """
        ⚠️ LƯU Ý QUAN TRỌNG: Đây là chế độ THỬ NGHIỆM (Dry-run). 
        Sau khi bạn đã điền xong tất cả thông tin biểu mẫu đăng tin (Tiêu đề, Mô tả, Giá, Diện tích, Địa chỉ, hình ảnh...), 
        TUYỆT ĐỐI KHÔNG được click vào nút "Đăng tin", "Hoàn tất" hoặc nút gửi form cuối cùng. 
        Hãy dừng lại ngay trước bước click gửi bài và báo cáo là đã điền form thành công.
        """
    else:
        dry_run_instruction = """
        LƯU Ý: Hãy điền đầy đủ thông tin và nhấn nút gửi bài đăng (Đăng tin/Hoàn tất) để xuất bản bài viết thực sự.
        """

    prompt = f"""
    Bạn là một trợ lý AI chuyên nghiệp điều khiển trình duyệt. Hãy thực hiện đăng tin bất động sản lên trang {args.site} theo các bước sau:

    Bước 1: Đi tới trang đăng nhập: {login_url}
    Bước 2: Điền thông tin tài khoản đăng nhập (chọn trường thích hợp dựa theo nhãn trên trang web):
       - Username: {username}
       - Email: {email}
       - Số điện thoại: {phone}
       - Mật khẩu: {password}
    Bước 3: Nhấn nút Đăng nhập. Nếu gặp thông báo thành công hoặc màn hình trang cá nhân thì tiếp tục bước sau.
    Bước 4: Tìm và nhấp vào nút "Đăng tin", "Đăng tin mới" hoặc "Đăng tin miễn phí".
    Bước 5: Điền các thông tin trong form đăng tin:
       - Tiêu đề: "{item.get('title')}"
       - Thể loại/Chuyên mục: Chọn "Cho thuê nhà đất" hoặc "Cho thuê văn phòng"
       - Nội dung chi tiết: "{item.get('content')}"
       - Giá: {item.get('price')} VNĐ (nếu form chỉ nhận số, hãy điền phần số thô)
       - Diện tích: {item.get('area')} m²
       - Tỉnh/Thành phố: Chọn "Đà Nẵng"
       - Quận/Huyện: Chọn "{item.get('district', 'Hải Châu')}"
       - Địa chỉ chi tiết: "{item.get('address')}"
       - Người liên hệ: "{item.get('contact_name', 'Nguyễn Ngọc Thiên Bình')}"
       - Số điện thoại liên hệ: "{item.get('phone', '0935723727')}"
    
    Bước 6: Tải lên các hình ảnh tin đăng sau (nếu form có hỗ trợ upload ảnh):
    {image_list_str if images else "Không có hình ảnh cụ thể để upload"}

    {dry_run_instruction}

    Bước cuối cùng: Chụp ảnh màn hình trạng thái form đã điền và báo cáo chi tiết kết quả.
    """

    print("\n🤖 Đang khởi tạo Browser-Use Agent...")
    browser = Browser(
        headless=args.headless,
        disable_security=True,
    )
    
    agent = Agent(
        task=prompt,
        llm=llm,
        browser=browser
    )

    print("🚀 Bắt đầu thực thi tác vụ...")
    try:
        history = await agent.run()
        print("\n🏁 Tác vụ kết thúc.")
        print(f"Kết quả cuối cùng của Agent: {history.final_result()}")
    except Exception as e:
        print(f"❌ Lỗi trong quá trình chạy Agent: {e}")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
