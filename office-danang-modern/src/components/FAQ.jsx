import React, { useState } from 'react';

const FAQS = [
  { q: 'Các dạng văn phòng cho thuê tại Đà Nẵng', a: 'Thị trường văn phòng Đà Nẵng hiện có nhiều loại hình như văn phòng truyền thống hạng A, B, C; văn phòng trọn gói, Coworking Space, văn phòng nguyên căn. Mỗi mô hình phù hợp với từng nhu cầu về ngân sách, quy mô nhân sự và thời gian thuê của doanh nghiệp.' },
  { q: 'Các diện tích văn phòng Đà Nẵng cho thuê?', a: 'Diện tích văn phòng cho thuê tại Đà Nẵng khá đa dạng, phổ biến từ 50m² đến hơn 1.000m². Các doanh nghiệp startup thường chọn diện tích dưới 100m², trong khi doanh nghiệp công nghệ, logistics hoặc FDI thường ưu tiên mặt bằng từ 300m² trở lên.' },
  { q: 'Giá thuê văn phòng tại Đà Nẵng bao nhiêu?', a: 'Giá thuê văn phòng tại Đà Nẵng hiện dao động khoảng $5 – $40/m²/tháng tùy hạng tòa nhà và vị trí. Văn phòng Hạng A: $20 – $40/m²/tháng. Văn phòng Hạng B: $10 – $20/m²/tháng. Văn phòng Hạng C: $5 – $10/m²/tháng.' },
  { q: 'Giờ làm việc và chi phí làm ngoài giờ tại Đà Nẵng như thế nào?', a: 'Hầu hết các tòa nhà văn phòng tại Đà Nẵng hoạt động từ 8h00 – 18h00 từ thứ 2 đến thứ 6 và sáng thứ 7. Nếu làm việc ngoài giờ, doanh nghiệp thường phát sinh thêm phí điều hòa và vận hành, dao động khoảng 50.000 – 150.000 VNĐ/giờ tùy tòa nhà.' },
  { q: 'Điều khoản thanh toán và đặt cọc khi thuê văn phòng Đà Nẵng?', a: 'Doanh nghiệp thuê văn phòng tại Đà Nẵng thường cần đặt cọc khoảng 3 tháng tiền thuê và thanh toán theo tháng hoặc quý. Ngoài tiền thuê, khách thuê cũng cần lưu ý thêm VAT, phí quản lý, phí gửi xe và chi phí điện điều hòa ngoài giờ.' },
  { q: 'Thời hạn thuê văn phòng Đà Nẵng tối thiểu bao lâu?', a: 'Thời hạn thuê văn phòng tại Đà Nẵng phổ biến từ 2 – 3 năm đối với văn phòng truyền thống. Riêng văn phòng trọn gói và Coworking Space có thể linh hoạt từ 6 – 12 tháng tùy nhu cầu doanh nghiệp.' },
  { q: 'Nên lưu ý gì khi ký hợp đồng thuê văn phòng Đà Nẵng?', a: 'Khi ký hợp đồng thuê văn phòng tại Đà Nẵng, doanh nghiệp nên kiểm tra kỹ diện tích tính phí, điều khoản tăng giá thuê, phí ngoài giờ, thời gian miễn phí thi công và điều kiện hoàn trả mặt bằng.' },
];

export default function FAQ() {
  const [faqOpen, setFaqOpen] = useState(null);

  return (
    <div className="faq-section" id="faq-section">
      <div className="container">
        <h2>Câu hỏi thường gặp khi thuê văn phòng tại Đà Nẵng</h2>
        <div className="faq-list">
          {FAQS.map((faq, i) => (
            <div className={`faq-item ${faqOpen === i ? 'open' : ''}`} key={i}>
              <button className="faq-question" onClick={() => setFaqOpen(faqOpen === i ? null : i)}>
                <span>{faq.q}</span>
                <span className="faq-chevron">▶</span>
              </button>
              {faqOpen === i && (
                <div className="faq-answer"><p>{faq.a}</p></div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
