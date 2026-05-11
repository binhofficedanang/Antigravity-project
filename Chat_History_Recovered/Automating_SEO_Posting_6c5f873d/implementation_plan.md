# Kế hoạch triển khai: Công cụ đăng bài SEO tự động (WP-SEO Bot)

Công cụ này sẽ giúp bạn tự động hóa hoàn toàn việc viết bài và đăng bài lên WordPress. Bạn chỉ cần nhập từ khóa, AI sẽ lo phần còn lại.

## User Review Required

> [!IMPORTANT]
> Để công cụ này hoạt động, bạn cần chuẩn bị:
> 1. **Gemini API Key**: Tôi sẽ hướng dẫn bạn lấy (miễn phí).
> 2. **WordPress Application Password**: Đây là mật khẩu đặc biệt để Python có thể đăng bài thay bạn (an toàn hơn mật khẩu chính).

## Proposed Changes

### Cấu trúc dự án mới

#### [NEW] config.json
Lưu trữ các cấu hình bảo mật:
- URL website WordPress.
- Username & Application Password.
- Gemini API Key.

#### [NEW] seo_generator.py
Chứa logic làm việc với Gemini AI:
- Prompt kỹ thuật để tạo bài viết có cấu trúc H1, H2, H3.
- Tự động tạo Meta Description và Thẻ Tag.
- Định dạng bài viết dưới dạng HTML để WordPress hiểu được.

#### [NEW] wp_publisher.py
Chứa logic kết nối WordPress REST API:
- Hàm `post_article()`: Đẩy nội dung lên web.
- Xử lý trạng thái (Draft hoặc Publish).

#### [NEW] main_seo.py
File điều khiển chính:
- Nhận danh sách từ khóa từ người dùng.
- Chạy vòng lặp: Viết bài -> Đăng bài.

---

## Các bước thực hiện

### 1. Chuẩn bị WordPress (Bạn cần làm)
1. Vào WordPress Admin > Users > Profile của bạn.
2. Tìm phần **Application Passwords**.
3. Nhập tên (ví dụ: "SEO-Bot") và bấm **Add New**. 
4. **Lưu lại mật khẩu 24 ký tự hiện ra.**

### 2. Cài đặt môi trường
Tôi sẽ cài thêm các thư viện cần thiết:
- `google-generativeai`
- `requests`

### 3. Lập trình module tạo nội dung
Sử dụng Gemini 1.5 Flash (nhanh và rẻ/miễn phí) để viết bài content dài > 1000 chữ chuẩn SEO.

### 4. Lập trình module đăng bài
Sử dụng phương thức `requests.post` với Basic Auth (Base64 encoded Application Password).

## Verification Plan

### Automated Tests
- Chạy script thử nghiệm đăng 1 bài ở chế độ "Draft" (Bản nháp) để kiểm tra định dạng.
- Kiểm tra tính đúng đắn của API Key.

### Manual Verification
- Bạn vào WordPress kiểm tra xem bài viết đã có đủ Tiêu đề, Nội dung, Thẻ Tag và Meta chưa.
