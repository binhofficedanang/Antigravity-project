# Tổng kết Bot Ngọa Long

Xin chúc mừng! Chúng ta đã xây dựng thành công một bot tự động thu thập tài nguyên cho game Ngọa Long trên Mac.

## Các công việc đã thực hiện

1. **Phân tích game**: Xác định Ngọa Long là Webgame chạy trên nền tảng Canvas/WebGL, do đó không thể dùng Javascript thông thường mà phải sử dụng kỹ thuật nhận diện hình ảnh.
2. **Khởi tạo môi trường**:
   - Sử dụng Python 3 có sẵn trên Mac.
   - Thiết lập môi trường ảo (`venv`) và cài đặt các thư viện lõi: `pyautogui` (điều khiển chuột) và `opencv-python` (nhận diện hình ảnh).
3. **Lập trình Logic Bot (`bot.py`)**:
   - Thay vì click ngẫu nhiên, bot được thiết kế để chạy theo một **Kịch bản (Sequence)** nghiêm ngặt gồm 22 bước do bạn định nghĩa.
   - Bot có khả năng chờ hình ảnh xuất hiện (tối đa 15 giây) để xử lý các độ trễ của game (lag/loading).
   - Hỗ trợ click nhiều lần liên tiếp vào cùng một tọa độ (ví dụ: `tangvangquockho` click 49 lần, `ruongnangdong` click 3 lần) với khoảng nghỉ siêu ngắn giữa các lần click.
4. **Cấu hình hình ảnh**: Thiết lập thư mục `targets` và liên kết 20 hình ảnh nút bấm với 22 bước của kịch bản.

## Hướng dẫn sử dụng lâu dài

Nếu bạn muốn thay đổi thứ tự click, thay đổi số lần click, hoặc thêm bớt các bước:
1. Mở file `bot.py` bằng bất kỳ trình soạn thảo văn bản nào (như TextEdit hoặc VS Code).
2. Tìm đến đoạn `SEQUENCE = [...]` và sửa lại danh sách.
3. Nếu thêm bước mới, nhớ chụp ảnh nút mới, cắt gọn gàng và bỏ vào thư mục `targets` với đuôi `.png`.

> [!TIP]
> **Tắt bot khẩn cấp:** Trong lúc bot đang chạy và cướp quyền điều khiển chuột, bạn hãy **cầm chuột và vuốt thật nhanh vào 1 trong 4 góc của màn hình**. Tính năng "Failsafe" của PyAutoGUI sẽ lập tức ngắt chương trình!
