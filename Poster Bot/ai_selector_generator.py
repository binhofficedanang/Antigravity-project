import asyncio
import os
import json
import argparse
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Nạp các biến môi trường
load_dotenv()

class SiteSelectors(BaseModel):
    login_url: str = Field(description="URL của trang đăng nhập")
    email_input: str = Field(description="CSS selector chính xác cho ô nhập Email/Tài khoản đăng nhập")
    password_input: str = Field(description="CSS selector chính xác cho ô nhập Mật khẩu")
    login_submit: str = Field(description="CSS selector chính xác cho nút Đăng nhập")
    
    post_url: str = Field(description="URL của trang đăng tin sau khi đăng nhập thành công")
    category_clicks: list[str] = Field(default=[], description="Mảng các CSS selector cần click theo thứ tự để chọn danh mục đăng tin bất động sản thuê thích hợp (ví dụ: nhấp chọn nhóm lớn rồi chọn nhóm con)")
    title_input: str = Field(description="CSS selector chính xác cho ô nhập Tiêu đề bài đăng")
    content_textarea: str = Field(description="CSS selector chính xác cho ô nhập Nội dung mô tả chi tiết")
    price_input: str = Field(description="CSS selector chính xác cho ô nhập Giá tiền")
    area_input: str = Field(description="CSS selector chính xác cho ô nhập Diện tích")
    image_upload: str = Field(description="CSS selector chính xác cho ô input file tải ảnh lên (thường là <input type='file'>)")
    submit_button: str = Field(description="CSS selector chính xác cho nút Gửi bài / Đăng tin cuối cùng")

def load_config(filepath="config.json"):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_selectors(site_name, selectors, filepath="selectors_db.json"):
    data = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    
    # AI có thể trả về SiteSelectors (Pydantic), dict, hoặc str (JSON cần parse)
    if isinstance(selectors, SiteSelectors):
        data[site_name] = selectors.model_dump()
    elif isinstance(selectors, dict):
        data[site_name] = selectors
    elif isinstance(selectors, str):
        try:
            data[site_name] = json.loads(selectors)
        except Exception:
            print(f"⚠️ Không parse được JSON từ chuỗi kết quả AI: {selectors[:200]}")
            return
    else:
        print(f"⚠️ Kiểu dữ liệu không hợp lệ từ AI: {type(selectors)}")
        return
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✓ Đã lưu selectors của trang [{site_name}] vào file {filepath}")

async def main():
    parser = argparse.ArgumentParser(description="AI Playwright Selector Generator")
    parser.add_argument("-s", "--site", type=str, default="raovat.net",
                        help="Trang web cần quét để sinh selectors")
    parser.add_argument("--headless", action="store_true",
                        help="Chạy ẩn danh")
    parser.add_argument("--llm", type=str, default="gemini", choices=["gemini", "ollama"],
                        help="Chọn LLM để chạy (gemini hoặc ollama)")
    parser.add_argument("--ollama-model", type=str, default="gemma4:e4b",
                        help="Tên mô hình Ollama (mặc định: gemma4:e4b)")
    args = parser.parse_args()

    print(f"=== BẮT ĐẦU QUÉT AI ĐỂ SINH SELECTORS CHO TRANG: {args.site} ===")

    # 1. Thiết lập LLM
    if args.llm == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            config = load_config()
            api_key = config.get("gemini_api_key") or config.get("GEMINI_API_KEY")
            if api_key:
                os.environ["GEMINI_API_KEY"] = api_key
            else:
                print("❌ Lỗi: GEMINI_API_KEY không được tìm thấy. Vui lòng định nghĩa trong file .env")
                return
        
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
                # Fallback sang ChatOpenAI sử dụng endpoint tương thích của Ollama
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

    # 2. Đọc tài khoản test từ config.json để đăng nhập
    config = load_config()
    site_config = config.get(args.site)
    if not site_config:
        print(f"❌ Không tìm thấy thông tin tài khoản cho trang {args.site} trong config.json")
        return
        
    username = site_config.get("username")
    email = site_config.get("email")
    phone = site_config.get("phone")
    password = site_config.get("password")
    
    login_credential = email or username or phone
    if not login_credential or not password:
        print(f"❌ Tài khoản hoặc mật khẩu trong config.json bị thiếu")
        return

    # 3. Import Agent và Browser từ browser-use
    try:
        from browser_use import Agent, Browser
    except ImportError as e:
        print(f"❌ Lỗi import browser-use: {e}")
        return

    login_url = f"https://{args.site}"
    if args.site == "raovat.net":
        login_url = "https://raovat.net/dang-nhap"
    elif args.site == "123nhadatviet.com":
        login_url = "https://123nhadatviet.com/dang-nhap.html"
    elif args.site == "thuviennhadat.vn":
        login_url = "https://thuviennhadat.vn/dang-nhap"

    prompt = f"""
    Mục tiêu của bạn là phân tích và tìm ra các CSS selector chính xác của trang web {args.site}.
    Hãy thực hiện các bước sau một cách cẩn thận:

    Bước 1: Đi tới trang đăng nhập: {login_url}
    Bước 2: Tìm CSS selector của ô nhập tài khoản (Email/Username/SĐT), ô mật khẩu và nút đăng nhập.
    Bước 3: Nhập thông tin tài khoản đăng nhập (Tài khoản: {login_credential}, Mật khẩu: {password}) và đăng nhập vào hệ thống.
    Bước 4: Sau khi đăng nhập thành công, tìm và click vào trang đăng tin (ví dụ: nút "Đăng tin", "Đăng tin miễn phí").
    Bước 5: Tại trang đăng tin, hãy quan sát biểu mẫu đăng tin (Form) và xác định CSS selector của:
       - Danh sách các selector cần click theo thứ tự để chọn được danh mục bất động sản cho thuê (ví dụ: nhấp chọn nhóm 'Nhà cửa đất đai' rồi chọn 'Thuê và cho thuê nhà', lưu các selector này theo đúng thứ tự vào mảng category_clicks)
       - Ô nhập tiêu đề tin đăng (title_input)
       - Ô nhập nội dung chi tiết (content_textarea)
       - Ô nhập giá (price_input)
       - Ô nhập diện tích (area_input)
       - Ô input tải tệp hình ảnh lên (image_upload - thường là thẻ <input type="file">)
       - Nút đăng tin cuối cùng để gửi form (submit_button)
    
    Hãy đảm bảo các CSS selector bạn tìm thấy là duy nhất và chính xác nhất để mã nguồn Playwright thuần có thể dùng trực tiếp bằng lệnh `page.fill(selector, text)` hoặc `page.click(selector)`.
    
    Sau khi đã tìm thấy đầy đủ selectors, hãy hoàn tất tác vụ và điền dữ liệu tương ứng vào cấu trúc output.
    """

    print("🤖 Đang khởi chạy AI Agent...")
    browser = Browser(
        headless=args.headless,
        disable_security=True,
    )

    agent = Agent(
        task=prompt,
        llm=llm,
        browser=browser,
        output_model_schema=SiteSelectors  # Sử dụng cấu trúc Pydantic để bắt AI trả về đúng định dạng
    )

    try:
        history = await agent.run()
        final_result = history.final_result()
        
        # Nếu AI trả về kết quả thành công dưới dạng JSON/Pydantic
        if final_result:
            print("\n🎉 AI đã phân tích và trích xuất thành công selectors!")
            save_selectors(args.site, final_result)
        else:
            print("❌ Không nhận được kết quả cấu trúc từ AI.")
    except Exception as e:
        print(f"❌ Lỗi trong quá trình chạy AI Agent: {e}")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
