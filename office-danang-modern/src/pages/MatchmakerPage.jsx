import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchBuildings } from '../utils/api';
import { useCompare } from '../context/CompareContext';

const questions = [
  {
    id: 'size',
    title: 'Quy mô nhân sự của công ty bạn? 👨‍👩‍👧‍👦',
    options: [
      { id: 'mini', text: 'Siêu nhỏ gọn (1 - 5 người)', icon: '🌱' },
      { id: 'small', text: 'Team tiêu chuẩn (6 - 20 người)', icon: '🚀' },
      { id: 'medium', text: 'Doanh nghiệp tầm trung (21 - 50 người)', icon: '🏢' },
      { id: 'large', text: 'Quy mô lớn (>50 người)', icon: '🏙️' },
    ]
  },
  {
    id: 'vibe',
    title: 'Phong cách làm việc bạn hướng đến? 🎯',
    options: [
      { id: 'quiet', text: 'Yên tĩnh, bảo mật, tập trung cao độ', icon: '🤫' },
      { id: 'creative', text: 'Không gian mở, sáng tạo (Coworking style)', icon: '🎨' },
      { id: 'professional', text: 'Chuyên nghiệp, chuẩn mực doanh nghiệp', icon: '👔' },
      { id: 'luxury', text: 'Sang chảnh, đẳng cấp để tiếp đối tác', icon: '💎' },
    ]
  },
  {
    id: 'budget',
    title: 'Ngân sách dự kiến của công ty? 💰',
    options: [
      { id: 'saving', text: 'Tối ưu chi phí (<$10/m²)', icon: '📉' },
      { id: 'balanced', text: 'Cân bằng chi phí & tiện ích ($10-$15/m²)', icon: '⚖️' },
      { id: 'premium', text: 'Cao cấp, tiện ích toàn diện ($15-$25/m²)', icon: '✨' },
      { id: 'unlimited', text: 'Không giới hạn, ưu tiên vị trí đắc địa (>$25/m²)', icon: '🚀' },
    ]
  },
  {
    id: 'location',
    title: 'Tiêu chí ưu tiên về vị trí & tiện ích? 📍',
    options: [
      { id: 'central', text: 'Trung tâm sầm uất, dễ tìm (Nguyễn Văn Linh, Lê Duẩn)', icon: '🏙️' },
      { id: 'river', text: 'View sông thoáng đãng (Bạch Đằng, Trần Hưng Đạo)', icon: '🌊' },
      { id: 'airport', text: 'Gần sân bay, bến xe (Thuận tiện đi công tác)', icon: '✈️' },
      { id: 'parking', text: 'Ưu tiên bãi đỗ xe rộng rãi cho nhân viên', icon: '🚗' },
    ]
  }
];

export default function MatchmakerPage() {
  const [step, setStep] = useState(0);
  const { toggleCompare, isSelected } = useCompare(); // 0: intro, 1-4: questions, 5: loading, 6: results
  const [answers, setAnswers] = useState({});
  const [matches, setMatches] = useState([]);
  const [allBuildings, setAllBuildings] = useState([]);
  const [showCompare, setShowCompare] = useState(false);

  useEffect(() => {
    fetchBuildings().then(data => setAllBuildings(data));
  }, []);

  const handleSelect = (questionId, optionId) => {
    setAnswers(prev => ({ ...prev, [questionId]: optionId }));
    
    if (step < questions.length) {
      setStep(step + 1);
    } else {
      calculateMatches();
    }
  };

  const calculateMatches = () => {
    setStep(5); // Loading
    
    setTimeout(() => {
      // Improved matching logic
      let scored = allBuildings.map(b => {
        let score = 0;
        const price = parseFloat(b.price) || 0;
        const address = (b.address || '').toLowerCase();
        const district = (b.district || '').toLowerCase();
        const grade = (b.grade || '').toUpperCase();

        // 1. NGÂN SÁCH (Max 25 điểm)
        if (answers.budget === 'saving') {
          if (price > 0 && price <= 11) score += 25;
          else if (price > 11 && price <= 15) score += 15;
          else score += 5; // Vẫn cho điểm vớt để không triệt tiêu các tiêu chí khác
        } else if (answers.budget === 'balanced') {
          if (price >= 11 && price <= 16) score += 25;
          else if (price >= 9 && price < 11) score += 20;
          else if (price > 16 && price <= 20) score += 15;
          else score += 5;
        } else if (answers.budget === 'premium') {
          if (price >= 16 && price <= 26) score += 25;
          else if (price > 26) score += 15;
          else if (price >= 13 && price < 16) score += 15;
          else score += 5;
        } else if (answers.budget === 'unlimited') {
          if (price >= 20) score += 25;
          else if (price >= 15 && price < 20) score += 15;
          else score += 10;
        }

        // 2. VỊ TRÍ & TIỆN ÍCH (Max 25 điểm)
        if (answers.location === 'river') {
          if (address.includes('bạch đằng') || address.includes('trần hưng đạo') || address.includes('như nguyệt')) score += 30; // Boost view sông
          else if (district.includes('hải châu') || district.includes('sơn trà')) score += 10;
        } else if (answers.location === 'central') {
          if (address.includes('nguyễn văn linh') || address.includes('lê duẩn') || address.includes('hùng vương')) score += 30;
          else if (district.includes('hải châu')) score += 15;
        } else if (answers.location === 'airport') {
          if (address.includes('nguyễn tri phương') || address.includes('điện biên phủ') || district.includes('thanh khê')) score += 30;
          else if (district.includes('hải châu')) score += 5;
        } else if (answers.location === 'parking') {
          if (grade === 'A') score += 30;
          else if (grade === 'B') score += 20;
          else score += 10;
        }

        // Lấy diện tích sàn để phân tích quy mô
        const floorArea = parseFloat((b.floorArea || '').toString().replace(/[^\d.]/g, '')) || 0;
        
        // Tìm năm xây dựng từ description (nếu có)
        const desc = (b.description || '').toLowerCase();
        let buildYear = 0;
        const yearMatch = desc.match(/(năm|xây dựng|hoàn thành).*?(20\d{2})/);
        if (yearMatch) buildYear = parseInt(yearMatch[2]);

        // 3. VIBE & PHONG CÁCH (Max 25 điểm)
        if (answers.vibe === 'luxury') {
          if (grade === 'A') score += 35; // Boost mạnh cho hạng A khi chọn Sang chảnh
          else if (grade === 'B') score += 15;
          else score += 0;
          
          if (buildYear >= 2022) score += 5;
          else if (buildYear >= 2018) score += 2;
        } else if (answers.vibe === 'professional') {
          if (grade === 'B') score += 25;
          else if (grade === 'A' || grade === 'C') score += 15;
        } else if (answers.vibe === 'creative') {
          if (b.name.toLowerCase().includes('coworking') || grade === 'C' || !grade) score += 25;
          else score += 10;
        } else if (answers.vibe === 'quiet') {
          if (grade === 'C' || district.includes('cẩm lệ') || district.includes('sơn trà')) score += 25;
          else score += 10;
        }

        // 4. QUY MÔ (Max 20 điểm - Giảm trọng số của quy mô xuống vì tòa nào cũng có thể chia nhỏ)
        if (answers.size === 'mini' || answers.size === 'small') {
          if (grade === 'C' || !grade) score += 20;
          else if (grade === 'B') score += 15;
          else if (grade === 'A') score += 10; // Hạng A vẫn có văn phòng chia sẻ/nhỏ
        } else if (answers.size === 'medium') {
          if (grade === 'B') score += 20;
          else score += 15;
        } else if (answers.size === 'large') {
          if (floorArea >= 300) score += 25; 
          else if (grade === 'A' || grade === 'B') score += 15; 
          else score += 5;
        }

        // Cộng một chút điểm ngẫu nhiên siêu nhỏ (0-2 điểm)
        score += Math.random() * 2;

        // Cap at 99
        if (score >= 99) score = 98 + Math.random();

        return { ...b, matchScore: score.toFixed(0) };
      });

      scored.sort((a, b) => b.matchScore - a.matchScore);
      setMatches(scored.slice(0, 6)); // Increased to 6 results
      setStep(6); // Results
    }, 2000);
  };

  return (
    <div className="matchmaker-page">
      <div className="container" style={{ padding: '40px 20px', maxWidth: '1000px', margin: '0 auto', minHeight: '80vh', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        
        {step === 0 && (
          <div className="mm-intro fadeIn" style={{ maxWidth: '800px', margin: '0 auto' }}>
            <h1>🤝 Office Matchmaker</h1>
            <p>Trải nghiệm tìm kiếm văn phòng thông minh! Trả lời 4 câu hỏi trắc nghiệm để hệ thống phân tích và đề xuất không gian làm việc tối ưu nhất cho doanh nghiệp của bạn.</p>
            <div className="mm-illustration">🔎🏢</div>
            <button className="btn-primary btn-large mm-btn" onClick={() => setStep(1)}>
              Bắt đầu Phân tích
            </button>
          </div>
        )}

        {step > 0 && step <= questions.length && (
          <div className="mm-quiz fadeIn" key={step} style={{ maxWidth: '800px', margin: '0 auto' }}>
            <div className="mm-progress">Bước {step} / {questions.length}</div>
            <h2>{questions[step - 1].title}</h2>
            <div className="mm-options">
              {questions[step - 1].options.map(opt => (
                <button 
                  key={opt.id} 
                  className="mm-option-btn"
                  onClick={() => handleSelect(questions[step - 1].id, opt.id)}
                >
                  <span className="mm-icon">{opt.icon}</span>
                  <span className="mm-text">{opt.text}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 5 && (
          <div className="mm-loading fadeIn">
            <div className="mm-heartbeat">⚙️</div>
            <h2>Đang phân tích dữ liệu...</h2>
            <p>Hệ thống đang quét qua 100+ tòa nhà văn phòng tại Đà Nẵng để tìm ra giải pháp tối ưu nhất cho bạn...</p>
          </div>
        )}

        {step === 6 && (
          <div className="mm-results fadeIn">
            <h1>🎉 Quá trình phân tích hoàn tất!</h1>
            <p>Dựa trên các tiêu chí bạn cung cấp, đây là 6 tòa nhà văn phòng phù hợp nhất:</p>
            
            <div className="mm-matches">
              {matches.map((b, index) => (
                <div key={b.id} className={`mm-match-card ${index === 0 ? 'top-match' : ''}`}>
                  <div className="match-badge">⭐ {b.matchScore}% Phù hợp</div>
                  <div style={{ position: 'relative' }}>
                    <img src={b.imageUrl || b.image || '/assets/modern_office_generic.jpg'} alt={b.name} style={{ width: '100%', display: 'block', borderRadius: '12px 12px 0 0' }} />
                    <div 
                      className={`compare-card-checkbox ${isSelected(b.id) ? 'active' : ''}`}
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        toggleCompare(b);
                      }}
                      title={isSelected(b.id) ? 'Xóa khỏi danh sách so sánh' : 'Thêm vào so sánh'}
                    >
                      <span className="compare-icon">{isSelected(b.id) ? '✓' : '+'}</span> So sánh
                    </div>
                  </div>
                  <div className="mm-match-info">
                    <h3>{b.name}</h3>
                    <p style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>📍 {b.address.replace(/,\s*(Thành phố |TP\.?\s*)?Đà Nẵng/gi, '')}</p>
                    <p className="mm-price">
                      💰 Giá: {parseFloat(b.price) > 0 ? `$${parseFloat(b.price)}/m²` : 'Liên hệ'}
                    </p>
                    <Link to={`/van-phong/${b.slug || b.id}`} className="btn-primary" style={{ width: '100%', marginTop: '12px' }}>
                      Xem chi tiết
                    </Link>
                  </div>
                </div>
              ))}
            </div>

            <div style={{ textAlign: 'center', marginTop: '30px' }}>
              <button 
                className="btn-outline" 
                onClick={() => setShowCompare(!showCompare)}
                style={{ fontSize: '1.1rem', padding: '12px 24px', borderRadius: '50px', background: 'white', color: 'var(--green)', borderColor: 'var(--border)', boxShadow: '0 4px 10px rgba(0,0,0,0.05)', fontWeight: 600, transition: 'all 0.3s' }}
              >
                {showCompare ? 'Thu Gọn Bảng So Sánh' : '📊 Xem Bảng So Sánh Chi Tiết Top 6'}
              </button>
            </div>

            {showCompare && (
              <div className="compare-table-responsive fadeIn" style={{ marginTop: '30px', background: 'white', padding: '20px', borderRadius: '16px', boxShadow: '0 10px 30px rgba(0,0,0,0.05)' }}>
                <table className="compare-table" style={{ width: '100%', minWidth: '800px' }}>
                  <thead>
                    <tr>
                      <th style={{ width: '120px', textAlign: 'left', padding: '15px' }}>Tiêu chí</th>
                      {matches.map(b => (
                        <th key={b.id} style={{ textAlign: 'center', padding: '15px 10px' }}>
                          <img src={b.imageUrl || b.image || '/assets/modern_office_generic.jpg'} alt={b.name} style={{ width: '100%', height: '80px', objectFit: 'cover', borderRadius: '8px', marginBottom: '10px' }} />
                          <div style={{ fontSize: '1rem', color: '#1e293b' }}>{b.name}</div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="compare-label-cell">Điểm Phù Hợp</td>
                      {matches.map(b => (
                        <td key={b.id} style={{ textAlign: 'center', fontWeight: 'bold', color: '#f59e0b', fontSize: '1.1rem' }}>⭐ {b.matchScore}%</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="compare-label-cell">Giá thuê (m²)</td>
                      {matches.map(b => (
                        <td key={b.id} className="compare-highlight-cell" style={{ textAlign: 'center' }}>
                          {parseFloat(b.price) > 0 ? `$${parseFloat(b.price)}` : 'Liên hệ'}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="compare-label-cell">Phân hạng</td>
                      {matches.map(b => (
                        <td key={b.id} style={{ textAlign: 'center' }}>
                          {b.grade ? <span className={`badge-grade grade-${b.grade}`}>{b.grade}</span> : '-'}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="compare-label-cell">Quận</td>
                      {matches.map(b => (
                        <td key={b.id} style={{ textAlign: 'center' }}>{b.district}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="compare-label-cell">Diện tích thuê</td>
                      {matches.map(b => (
                        <td key={b.id} style={{ textAlign: 'center', fontSize: '0.9rem' }}>{b.availableAreas || 'Đang cập nhật'}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="compare-label-cell">Hành động</td>
                      {matches.map(b => (
                        <td key={b.id} style={{ textAlign: 'center' }}>
                          <Link to={`/van-phong/${b.slug || b.id}`} className="compare-view-detail-btn" style={{ display: 'inline-block', padding: '6px 12px', fontSize: '0.9rem' }}>Chi Tiết</Link>
                        </td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
            
            <div className="mm-cta-section" style={{ background: 'linear-gradient(135deg, var(--green) 0%, var(--green-dark) 100%)', color: 'white', padding: '40px', borderRadius: '16px', marginTop: '50px', textAlign: 'center', boxShadow: '0 20px 40px rgba(227,28,95,0.2)' }}>
              <h2>🤔 Bạn cần phương án tối ưu hơn?</h2>
              <p style={{ fontSize: '1.1rem', marginBottom: '24px', color: 'rgba(255,255,255,0.9)', lineHeight: 1.6 }}>Bài trắc nghiệm này chỉ là bước sàng lọc ban đầu. Hãy để chuyên gia tư vấn 10+ năm kinh nghiệm của Office43 giúp bạn tìm các diện tích "Off-market", phân tích phong thủy chuyên sâu và đàm phán mức giá tốt nhất hoàn toàn miễn phí.</p>
              <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
                <Link to="/lien-he" className="btn-primary" style={{ background: 'white', color: 'var(--green-dark)', border: 'none', padding: '14px 28px', fontSize: '1.1rem', fontWeight: 600, borderRadius: '50px', boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>📞 Liên Hệ Chuyên Gia Tư Vấn</Link>
                <button className="btn-outline" onClick={() => { setStep(1); setAnswers({}); }} style={{ background: 'transparent', borderColor: 'white', color: 'white', padding: '14px 28px', fontSize: '1.1rem', fontWeight: 600, borderRadius: '50px' }}>
                  🔄 Làm Lại Khảo Sát
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
