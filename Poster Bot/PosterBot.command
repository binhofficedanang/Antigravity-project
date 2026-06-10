#!/bin/bash
# Tự động chuyển thư mục Terminal về thư mục chứa file script này
cd "$(dirname "$0")"

echo "=================================================================="
echo "   🏢 ĐANG KHỞI ĐỘNG HỆ THỐNG ĐĂNG TIN POSTER BOT DASHBOARD...   "
echo "=================================================================="
echo "📍 Thư mục làm việc: $(pwd)"
echo "🚀 Đang khởi động Server Streamlit..."
echo "🌐 Trình duyệt Safari/Chrome sẽ tự động mở trang Dashboard sau vài giây."
echo "------------------------------------------------------------------"

# Chạy server Streamlit cục bộ bằng Python Virtual Environment
../venv/bin/streamlit run app.py

# Giữ cửa sổ terminal nếu có lỗi khởi động
echo ""
echo "------------------------------------------------------------------"
echo "⚠️ Server đã dừng. Nhấn phím bất kỳ để đóng cửa sổ này..."
read -n 1
