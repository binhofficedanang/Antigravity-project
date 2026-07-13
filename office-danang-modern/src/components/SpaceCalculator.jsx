import React, { useState } from 'react';

export default function SpaceCalculator() {
  const [employees, setEmployees] = useState(20);
  const [spaceType, setSpaceType] = useState('standard'); 
  const [isOpen, setIsOpen] = useState(false);
  
  // Các hệ số diện tích m2 / người (khoảng)
  const spaceMultiplier = {
    'startup': { min: 3.5, max: 5 },    // Tối ưu diện tích
    'standard': { min: 5, max: 7 },     // Tiêu chuẩn
    'premium': { min: 7, max: 10 }      // Rộng rãi, cao cấp (nhiều không gian chung)
  };

  // Ước tính giá trung bình $/m2/tháng (khoảng)
  const priceEstimates = {
    'startup': { min: 9, max: 12 },
    'standard': { min: 13, max: 18 },
    'premium': { min: 18, max: 30 }
  };

  const minArea = Math.round(employees * spaceMultiplier[spaceType].min);
  const maxArea = Math.round(employees * spaceMultiplier[spaceType].max);
  
  const minBudget = minArea * priceEstimates[spaceType].min;
  const maxBudget = maxArea * priceEstimates[spaceType].max;

  if (!isOpen) {
    return (
      <div style={{ textAlign: 'center', margin: '20px 0 40px' }}>
        <button 
          className="btn-outline" 
          style={{ display: 'inline-flex', alignItems: 'center', gap: '10px', padding: '14px 28px', fontSize: '1.1rem', borderRadius: '50px', fontWeight: 600, border: '2px solid var(--primary)', color: 'var(--primary)' }}
          onClick={() => setIsOpen(true)}
        >
          <span>📐</span> Bật Công Cụ Tính Diện Tích & Ngân Sách
        </button>
      </div>
    );
  }

  return (
    <div className="space-calculator fadeIn" style={{ position: 'relative' }}>
      <button 
        onClick={() => setIsOpen(false)} 
        style={{ position: 'absolute', top: '24px', right: '24px', background: '#f1f5f9', border: 'none', width: '36px', height: '36px', borderRadius: '50%', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', color: '#64748b', transition: 'all 0.2s' }}
        onMouseEnter={(e) => { e.currentTarget.style.background = '#e2e8f0'; e.currentTarget.style.color = '#334155'; }}
        onMouseLeave={(e) => { e.currentTarget.style.background = '#f1f5f9'; e.currentTarget.style.color = '#64748b'; }}
        title="Đóng công cụ"
      >
        ✕
      </button>
      <div className="calc-header">
        <h3>📐 Tính Toán Diện Tích & Ngân Sách</h3>
        <p>Công cụ ước tính nhanh không gian làm việc phù hợp cho doanh nghiệp của bạn.</p>
      </div>
      <div className="calc-body">
        <div className="calc-inputs">
          <div className="calc-group">
            <label>Số lượng nhân sự:</label>
            <div className="calc-range-wrapper">
              <input 
                type="range" 
                min="5" max="200" step="1" 
                value={employees} 
                onChange={(e) => setEmployees(parseInt(e.target.value))} 
              />
              <div className="calc-value">{employees} người</div>
            </div>
          </div>
          <div className="calc-group">
            <label>Mô hình văn phòng:</label>
            <div className="calc-pills">
              <button 
                className={`calc-pill ${spaceType === 'startup' ? 'active' : ''}`}
                onClick={() => setSpaceType('startup')}
              >
                Tiết kiệm
              </button>
              <button 
                className={`calc-pill ${spaceType === 'standard' ? 'active' : ''}`}
                onClick={() => setSpaceType('standard')}
              >
                Tiêu chuẩn
              </button>
              <button 
                className={`calc-pill ${spaceType === 'premium' ? 'active' : ''}`}
                onClick={() => setSpaceType('premium')}
              >
                Cao cấp
              </button>
            </div>
          </div>
        </div>
        <div className="calc-results">
          <div className="result-box">
            <h4>Diện tích đề xuất</h4>
            <div className="result-val highlight">{minArea} - {maxArea} <span>m²</span></div>
            <div className="result-sub">Khoảng {spaceMultiplier[spaceType].min} - {spaceMultiplier[spaceType].max} m²/người</div>
          </div>
          <div className="result-box">
            <h4>Ngân sách dự kiến</h4>
            <div className="result-val">${minBudget.toLocaleString()} - ${maxBudget.toLocaleString()} <span>/tháng</span></div>
            <div className="result-sub">Mức giá trung bình ${priceEstimates[spaceType].min} - ${priceEstimates[spaceType].max}/m²</div>
          </div>
        </div>
      </div>
    </div>
  );
}
