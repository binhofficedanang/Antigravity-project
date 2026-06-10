import matplotlib.pyplot as plt
import numpy as np
import os

class SEOChartGenerator:
    def __init__(self, output_dir="."):
        self.output_dir = output_dir
        # Đảm bảo thư mục tồn tại
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_price_comparison(self, filename="bang-gia-thue-van-phong-da-nang.png", title="So Sánh Giá Thuê Văn Phòng Theo Quận tại Đà Nẵng ($/m2)"):
        # Dữ liệu mô phỏng
        districts = ['Hải Châu', 'Thanh Khê', 'Sơn Trà', 'Cẩm Lệ', 'Ngũ Hành Sơn']
        min_prices = [12, 8, 10, 6, 9]
        max_prices = [35, 15, 20, 12, 18]

        x = np.arange(len(districts))
        width = 0.35

        # Thiết lập style đồ thị
        plt.style.use('ggplot') # Hoặc fivethirtyeight
        fig, ax = plt.subplots(figsize=(10, 6))

        rects1 = ax.bar(x - width/2, min_prices, width, label='Giá thấp nhất', color='#6366f1')
        rects2 = ax.bar(x + width/2, max_prices, width, label='Giá cao nhất', color='#22c55e')

        # Thêm nhãn, tiêu đề
        ax.set_ylabel('Giá thuê ($/m2/tháng)', fontsize=12)
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(districts, fontsize=11)
        ax.legend()

        # Thêm số trên cột
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f'${height}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom', fontweight='bold')

        autolabel(rects1)
        autolabel(rects2)

        # Thêm watermark
        fig.text(0.5, 0.02, 'Nguồn dữ liệu: Office Danang (officedanang.vn)', ha='center', fontsize=10, color='gray', style='italic')

        fig.tight_layout()
        
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Đã tạo biểu đồ thành công: {filepath}")
        return filepath

if __name__ == "__main__":
    generator = SEOChartGenerator(output_dir="charts")
    generator.generate_price_comparison()
