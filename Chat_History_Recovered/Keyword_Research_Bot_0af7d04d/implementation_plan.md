# Kế hoạch nâng cấp: Tăng chất lượng bài viết và Tính năng chọn lọc từ khóa

## Vấn đề hiện tại
1. **Sai năm & Chất lượng thấp**: Bài viết sinh ra đang mang văn phong cũ và ghi năm 2024. Điều này xảy ra do AI mặc định kiến thức theo tập dữ liệu cũ nếu không được nhắc nhở.
2. **Không được chọn từ khóa**: Bot nghiên cứu tự động lưu toàn bộ từ khóa vào file, khiến bạn không thể loại bỏ các từ khóa không ưng ý trước khi viết bài.

## Proposed Changes

### 1. Nâng cấp chất lượng bài viết và cập nhật thời gian
#### [MODIFY] [SEO bot/seo_generator.py](file:///Users/binhihi/Desktop/Antigravity/SEO%20bot/seo_generator.py)
- Bổ sung vào **Prompt Engineering** một dòng lệnh "ép buộc" (System Instruction) yêu cầu AI nhận thức năm hiện tại là **2026**.
- Ra lệnh cho AI phải cập nhật văn phong, xu hướng và thông tin (giá cả, thị trường) theo bối cảnh năm 2026.
- Thêm yêu cầu hành văn tự nhiên, chuyên sâu như một chuyên gia thực thụ để tăng chất lượng đầu ra.

### 2. Thêm tính năng chọn lọc từ khóa vào Bot Nghiên cứu
#### [MODIFY] [Keyword Research Bot/researcher.py](file:///Users/binhihi/Desktop/Antigravity/Keyword%20Research%20Bot/researcher.py)
- Sau khi AI sinh ra danh sách từ khóa, thay vì lưu ngay vào file `content_plan.json`, script sẽ in ra màn hình danh sách các từ khóa kèm số thứ tự (1, 2, 3...).
- Hiển thị dòng nhắc (Prompt Input) để bạn nhập các số thứ tự bạn muốn chọn (ví dụ: `1,3,4` hoặc `all` để chọn tất cả).
- Script sẽ lọc lại danh sách và chỉ lưu những từ khóa bạn đã chọn vào file kế hoạch.

## User Review Required
> [!IMPORTANT]
> - Đối với tính năng chọn từ khóa: Bạn sẽ nhập số thứ tự các bài muốn giữ lại (VD: `1, 3, 5`) bằng cách gõ tay. Bạn có đồng ý với thiết kế giao diện dòng lệnh này không?
> - Ngoài việc ép thời gian là "Năm 2026", bạn có muốn bot SEO đóng vai trò cụ thể nào không (VD: "Chuyên gia bất động sản 10 năm kinh nghiệm tại Đà Nẵng") để giọng văn hay hơn? Mặc định tôi sẽ thiết lập văn phong chuyên gia.
