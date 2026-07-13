import React, { useState } from 'react';
import { useCompare } from '../context/CompareContext';

export default function CompareTool() {
  const { selectedBuildings, toggleCompare, clearCompare } = useCompare();
  const [isOpen, setIsOpen] = useState(false);

  if (selectedBuildings.length === 0) return null;

  return (
    <>
      {/* Floating compare status bar at the bottom */}
      <div className="compare-bar shadow">
        <div className="compare-bar-container">
          <div className="compare-bar-info">
            <span className="compare-count">{selectedBuildings.length}</span>
            <span className="compare-label">Tòa nhà được chọn so sánh</span>
          </div>
          
          <div className="compare-thumbs">
            {selectedBuildings.map((b) => (
              <div key={b.id} className="compare-thumb-item">
                <img src={b.imageUrl || b.image || '/assets/modern_office_generic.jpg'} alt={b.name} />
                <button 
                  className="compare-remove-btn" 
                  onClick={(e) => { e.stopPropagation(); toggleCompare(b); }}
                  title="Xóa khỏi danh sách so sánh"
                >
                  ×
                </button>
              </div>
            ))}
            {selectedBuildings.length < 3 && (
              <div className="compare-thumb-placeholder">
                <span>+ Chọn thêm</span>
              </div>
            )}
          </div>

          <div className="compare-actions">
            <button className="compare-clear-btn" onClick={clearCompare}>Xóa tất cả</button>
            <button 
              className="compare-trigger-btn animate-pulse" 
              onClick={() => setIsOpen(true)}
              disabled={selectedBuildings.length < 2}
              title={selectedBuildings.length < 2 ? 'Chọn ít nhất 2 tòa nhà để so sánh' : 'So sánh ngay'}
            >
              So Sánh Ngay
            </button>
          </div>
        </div>
      </div>

      {/* Comparison Detail Overlay Modal */}
      {isOpen && (
        <div className="compare-overlay" onClick={() => setIsOpen(false)}>
          <div className="compare-modal animate-fade-in" onClick={(e) => e.stopPropagation()}>
            <div className="compare-modal-header">
              <h2>So Sánh Thông Số Văn Phòng</h2>
              <button className="compare-close-modal" onClick={() => setIsOpen(false)}>×</button>
            </div>
            
            <div className="compare-modal-body">
              <div className="compare-table-responsive">
                <table className="compare-table">
                  <thead>
                    <tr>
                      <th style={{ width: '20%' }}>Thông số</th>
                      {selectedBuildings.map((b) => (
                        <th key={b.id} style={{ width: `${80 / selectedBuildings.length}%` }}>
                          <div className="compare-header-card">
                            <img 
                              className="compare-card-img" 
                              src={b.imageUrl || b.image || '/assets/modern_office_generic.jpg'} 
                              alt={b.name} 
                            />
                            <h3>{b.name}</h3>
                            <button className="btn-remove-cell" onClick={() => toggleCompare(b)}>
                              Loại bỏ
                            </button>
                          </div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="compare-label-cell">Địa chỉ</td>
                      {selectedBuildings.map((b) => (
                        <td key={b.id}>{b.address}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="compare-label-cell">Phân hạng</td>
                      {selectedBuildings.map((b) => (
                        <td key={b.id}>
                          <span className={`badge-grade grade-${b.grade}`}>{b.grade}</span>
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="compare-label-cell">Giá thuê (m²/tháng)</td>
                      {selectedBuildings.map((b) => (
                        <td key={b.id} className="compare-highlight-cell">
                          {parseFloat(b.price) > 0 ? `$${b.price}` : 'Liên hệ'}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="compare-label-cell">Phí dịch vụ</td>
                      {selectedBuildings.map((b) => (
                        <td key={b.id}>
                          {parseFloat(b.serviceCharge) > 0 ? `$${b.serviceCharge}` : 'Miễn phí / Đã bao gồm'}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="compare-label-cell">Diện tích thuê</td>
                      {selectedBuildings.map((b) => (
                        <td key={b.id}>{b.availableAreas || 'Đang cập nhật'}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="compare-label-cell">Phí đỗ xe máy</td>
                      {selectedBuildings.map((b) => (
                        <td key={b.id}>{b.parkingFee || 'Liên hệ'}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="compare-label-cell">Phí đỗ ô tô</td>
                      {selectedBuildings.map((b) => (
                        <td key={b.id}>{b.carParkingFee || 'Liên hệ'}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="compare-label-cell">Hành động</td>
                      {selectedBuildings.map((b) => (
                        <td key={b.id}>
                          <a 
                            href={`/van-phong/${b.id}`} 
                            className="compare-view-detail-btn"
                          >
                            Xem Chi Tiết
                          </a>
                        </td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
