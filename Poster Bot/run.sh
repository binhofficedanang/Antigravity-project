#!/bin/bash

# Di chuyển vào thư mục của script
cd "$(dirname "$0")"

# Mặc định chạy bot đăng bài tiếp theo
# Nếu truyền tham số --crawl (e.g. ./run.sh --crawl), bot sẽ cào tin mới trước khi đăng
if [ "$1" == "--crawl" ]; then
    echo "=========================================="
    echo "🔍 Đang tiến hành cào và xào tin mới..."
    echo "=========================================="
    ../venv/bin/python3 extract_buildings.py --pages 2 --apply
    echo ""
fi

echo "=========================================="
echo "🚀 Đang khởi động bot đăng tin tiếp theo..."
echo "=========================================="
../venv/bin/python3 main.py
