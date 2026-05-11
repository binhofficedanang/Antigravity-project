# Hướng dẫn Tính năng mới: Chọn lọc Từ khóa & Cập nhật bài viết 2026

Toàn bộ quá trình nâng cấp hệ thống đã hoàn tất. Sau đây là những thay đổi lớn giúp bạn kiểm soát chất lượng Content tốt hơn bao giờ hết.

## 1. Tính năng Chọn lọc Từ khóa (Researcher Bot)

Giờ đây, Bot Nghiên cứu sẽ **KHÔNG TỰ ĐỘNG LƯU** toàn bộ từ khóa như trước nữa. Thay vào đó, nó sẽ cho phép bạn làm "Tổng biên tập".

**Cách hoạt động mới:**
1. Chạy lệnh: `python researcher.py`
2. Nhập chủ đề bạn muốn. AI sẽ sinh ra danh sách (VD: 10 từ khóa) và in lên màn hình kèm số thứ tự `[1]`, `[2]`, `[3]`...
3. Bot sẽ tạm dừng và hỏi bạn: `Nhập các số thứ tự bạn muốn CHỌN (Ví dụ: 1,3,4)`
   - Nếu bạn chỉ ưng ý bài 1, bài 3, bài 5: **Gõ `1,3,5` rồi Enter**.
   - Nếu bạn thấy danh sách này quá xuất sắc và muốn giữ lại tất cả: **Gõ `all` (hoặc cứ thế nhấn Enter)**.
   - Nếu bạn thấy kết quả quá tệ, không muốn lưu: **Gõ `0`**.
4. Bot sẽ chỉ lưu những từ khóa bạn đã duyệt vào file Kế hoạch để SEO Bot đi viết bài.

## 2. Nâng cấp Chất lượng Bài viết (SEO Bot)

Nhờ cập nhật lại Prompt gốc của file `seo_generator.py`, từ nay các bài viết sinh ra sẽ có những đặc điểm sau:
- **Đóng vai Chuyên gia:** Bot sẽ viết bài dưới góc nhìn của một "Chuyên gia Môi giới và Đầu tư Bất động sản với hơn 10 năm kinh nghiệm". Giọng văn sẽ cực kỳ chuyên sâu, uy tín và thuyết phục.
- **Dữ liệu mới nhất (Năm 2026):** Tôi đã thiết lập lệnh ép buộc AI phải sử dụng bối cảnh năm **2026**. Bạn sẽ không bao giờ thấy tình trạng bài viết xuất hiện các mốc thời gian cũ như 2024 hay 2025 nữa.

---

> [!TIP]
> Bạn hãy thử chạy lệnh dưới đây để trải nghiệm ngay cảm giác "chốt" từ khóa nhé:
> ```bash
> cd "/Users/binhihi/Desktop/Antigravity/Keyword Research Bot" && source ../venv/bin/activate && python researcher.py
> ```
