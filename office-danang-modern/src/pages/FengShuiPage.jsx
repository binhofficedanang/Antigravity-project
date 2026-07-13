import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchBuildings } from '../utils/api';

export default function FengShuiPage() {
  const [year, setYear] = useState('');
  const [gender, setGender] = useState('male');
  const [result, setResult] = useState(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const [recommendedBuildings, setRecommendedBuildings] = useState([]);
  const [allBuildings, setAllBuildings] = useState([]);

  useEffect(() => {
    fetchBuildings().then(data => {
      setAllBuildings(data);
    });
  }, []);

  const calculateFengShui = (e) => {
    e.preventDefault();
    if (!year || year < 1920 || year > 2024) return;
    
    setIsAnimating(true);
    setResult(null);

    // Simulated delay for animation
    setTimeout(() => {
      const y = parseInt(year);
      
      // Calculate Mệnh (Element)
      const canMap = { 0:4, 1:4, 2:5, 3:5, 4:1, 5:1, 6:2, 7:2, 8:3, 9:3 };
      const chiMap = { 0:1, 1:1, 2:2, 3:2, 4:0, 5:0, 6:1, 7:1, 8:2, 9:2, 10:0, 11:0 };
      
      let canValue = canMap[y % 10];
      let chiValue = chiMap[y % 12];
      
      let menhValue = canValue + chiValue;
      if (menhValue > 5) menhValue -= 5;
      
      const elements = {
        1: { name: 'Kim', colors: 'Trắng, Xám, Ghi, Vàng, Nâu', directions: 'Tây, Tây Bắc, Tây Nam, Đông Bắc', desc: 'Quyết đoán, kiên định. Hợp với các văn phòng thiết kế hiện đại, nhiều kính và kim loại.' },
        2: { name: 'Thủy', colors: 'Đen, Xanh nước biển, Trắng, Ghi', directions: 'Bắc, Đông, Nam, Đông Nam', desc: 'Linh hoạt, nhạy bén. Rất hợp với các văn phòng view sông, gần nước hoặc có thiết kế mềm mại.' },
        3: { name: 'Hỏa', colors: 'Đỏ, Cam, Hồng, Tím, Xanh lá', directions: 'Nam, Đông, Đông Nam, Bắc', desc: 'Nhiệt huyết, sáng tạo. Nên chọn văn phòng nhiều ánh sáng tự nhiên, không gian mở năng động.' },
        4: { name: 'Thổ', colors: 'Vàng, Nâu, Đỏ, Cam, Hồng', directions: 'Đông Bắc, Tây Nam', desc: 'Vững vàng, đáng tin cậy. Hợp với các tòa nhà có kiến trúc vuông vức, vững chãi, chất liệu đá/gạch.' },
        5: { name: 'Mộc', colors: 'Xanh lá, Xanh nước biển, Đen', directions: 'Đông, Đông Nam, Nam, Bắc', desc: 'Phát triển, bao dung. Rất tốt nếu văn phòng có nhiều cây xanh, nội thất gỗ mộc mạc.' }
      };
      
      const element = elements[menhValue];
      setResult(element);
      setIsAnimating(false);

      // Randomly pick 3 buildings for fun recommendation
      if (allBuildings.length > 0) {
        const shuffled = [...allBuildings].sort(() => 0.5 - Math.random());
        setRecommendedBuildings(shuffled.slice(0, 3));
      }
    }, 1500); // 1.5s spinning animation
  };

  return (
    <div className="fengshui-page">
      <div className="fengshui-hero">
        <div className="container">
          <h1>🧭 La Bàn Phong Thủy Văn Phòng</h1>
          <p>Tìm hướng ngồi, màu sắc tài lộc và văn phòng "hợp mệnh" giúp doanh nghiệp của bạn phát đạt!</p>
        </div>
      </div>

      <div className="container" style={{ padding: '40px 20px', maxWidth: '800px', margin: '0 auto' }}>
        <div className="fengshui-card">
          <form onSubmit={calculateFengShui} className="fengshui-form">
            <div className="form-group">
              <label>Năm sinh (Founder/CEO):</label>
              <input type="number" value={year} onChange={e => setYear(e.target.value)} placeholder="Ví dụ: 1990" required />
            </div>
            <div className="form-group">
              <label>Giới tính:</label>
              <select value={gender} onChange={e => setGender(e.target.value)}>
                <option value="male">Nam</option>
                <option value="female">Nữ</option>
              </select>
            </div>
            <button type="submit" className="btn-primary btn-large" disabled={isAnimating}>
              {isAnimating ? 'Đang xoay la bàn...' : 'Xem Kết Quả Ngay!'}
            </button>
          </form>

          {isAnimating && (
            <div className="compass-container">
              <div className="compass-spin">🧭</div>
              <p>Đang tính toán ngũ hành...</p>
            </div>
          )}

          {result && !isAnimating && (
            <div className="fengshui-result fadeIn">
              <div className="result-header">
                <h2>Chủ doanh nghiệp mệnh <span className="menh-highlight">{result.name}</span></h2>
                <p>{result.desc}</p>
              </div>
              
              <div className="result-grid-fs">
                <div className="result-box-fs">
                  <div className="icon-fs">🎨</div>
                  <h3>Màu sắc may mắn</h3>
                  <p>{result.colors}</p>
                  <small>Dùng cho màu chủ đạo logo, nội thất</small>
                </div>
                <div className="result-box-fs">
                  <div className="icon-fs">🚪</div>
                  <h3>Hướng tốt</h3>
                  <p>{result.directions}</p>
                  <small>Đón tài lộc, vượng khí cho công ty</small>
                </div>
              </div>

              {recommendedBuildings.length > 0 && (
                <div className="recommended-buildings-fs">
                  <h3>🏢 Các tòa nhà "Hợp Vía" đề xuất cho bạn</h3>
                  <div className="building-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginTop: '20px' }}>
                    {recommendedBuildings.map(b => (
                      <Link to={`/van-phong/${b.slug}`} key={b.id} className="building-card" style={{ display: 'block', textDecoration: 'none' }}>
                        <div className="building-card-img" style={{ height: '150px' }}>
                          <img src={b.image || '/assets/modern_office_generic.jpg'} alt={b.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        </div>
                        <div className="building-card-content" style={{ padding: '12px' }}>
                          <h4 style={{ fontSize: '1rem', margin: '0 0 8px 0', color: '#333' }}>{b.name}</h4>
                          <p style={{ fontSize: '0.85rem', color: '#666', margin: 0 }}>📍 {b.district}</p>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
