# Kế hoạch Triển khai: Giai đoạn 2 (Multi-Account)

Việc mở rộng bot để cày nhiều tài khoản (Multi-Account) là một nâng cấp lớn. Đối với bot nhận diện hình ảnh (PyAutoGUI), chúng ta có 2 chiến lược chính.

## User Review Required

> [!WARNING]
> Bạn vui lòng đọc kỹ 2 phương án dưới đây và chọn 1 phương án phù hợp nhất với cấu hình máy Mac và thói quen chơi game của bạn.

### Phương án A: Chạy Tuần tự (Lần lượt từng nick)
- **Cách hoạt động**: Mở 1 tab trình duyệt. Bot tự động gõ Tài khoản 1 -> Đăng nhập -> Cày hết kịch bản -> Bấm Đăng xuất -> Gõ Tài khoản 2 -> Đăng nhập -> Cày...
- **Ưu điểm**: Nhẹ máy, an toàn, dễ kiểm soát, màn hình không bị rối.
- **Nhược điểm**: Mất thời gian lâu hơn nếu bạn có hàng chục tài khoản.
- **Yêu cầu thêm**: Bạn cần cung cấp danh sách file chứa tài khoản/mật khẩu, và chụp thêm các ảnh nút "Đăng nhập", ô "Nhập username", "Đăng xuất"...

### Phương án B: Chạy Song song (Mở nhiều cửa sổ cùng lúc)
- **Cách hoạt động**: Bạn tự tay mở 2, 3 hoặc 4 cửa sổ trình duyệt thu nhỏ cạnh nhau trên màn hình, mỗi cửa sổ đăng nhập sẵn 1 tài khoản. Bot sẽ được nâng cấp từ "tìm 1 nút" thành **"quét toàn bộ màn hình và bấm vào tất cả các nút giống nhau"** (Dùng lệnh `locateAllOnScreen`).
- **Ưu điểm**: Siêu nhanh. Cày 4 nick cùng lúc chỉ tốn thời gian bằng cày 1 nick.
- **Nhược điểm**: Phụ thuộc vào độ lớn của màn hình Mac. Nếu mở quá nhiều cửa sổ, hình ảnh trong game sẽ bị thu nhỏ lại tới mức bot không thể nhận diện được. Rất ngốn RAM máy tính.

## Open Questions

> [!CAUTION]
> 1. Bạn chọn **Phương án A** hay **Phương án B**?
> 2. Nếu chọn A: Bạn có muốn tôi tạo file `accounts.txt` để bạn nhập ID/Pass không? PyAutoGUI có thể giả lập bàn phím để tự gõ phím.
> 3. Nếu chọn B: Màn hình Mac của bạn có đủ to để mở nhiều cửa sổ cạnh nhau mà các nút bấm vẫn hiển thị rõ ràng không?

## Proposed Changes
Dựa vào lựa chọn của bạn, tôi sẽ tiến hành đập đi xây lại cấu trúc vòng lặp của file `bot.py` để hỗ trợ cơ chế mới.
