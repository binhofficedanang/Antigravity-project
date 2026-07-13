import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchBuildings } from '../utils/api';
import { useSEO } from '../utils/seo';
import BuildingCard from '../components/BuildingCard';
import ContactForm from '../components/ContactForm';

// Convert any string to URL slug (remove diacritics)
function toSlug(str) {
  return (str || '')
    .toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

export default function WardPage() {
  const { wardName } = useParams();
  const [buildingsData, setBuildingsData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBuildings().then(data => {
      setBuildingsData(data);
      setLoading(false);
    });
    window.scrollTo(0, 0);
  }, [wardName]);

  const filteredBuildings = useMemo(() => {
    // So sánh theo slug (không dấu) để tránh lệch Unicode giữa Hoà/Hòa
    return buildingsData.filter(b => b.district && toSlug(b.district) === toSlug(wardName || ''));
  }, [buildingsData, wardName]);

  // Actual exact name from data (e.g. "Phường Hải Châu")
  const actualWardName = filteredBuildings.length > 0 ? filteredBuildings[0].district : (wardName || '').replace(/-/g, ' ');
  
  // Clean prefix to prevent duplicates like "Phường Phường Hải Châu"
  const cleanWardName = actualWardName.replace(/^(Phường|P\.)\s+/i, '');

  // Calculate dynamic stats for SEO and UI
  const stats = useMemo(() => {
    if (filteredBuildings.length === 0) return null;
    const total = filteredBuildings.length;
    const validPrices = filteredBuildings
      .map(b => parseFloat(b.price))
      .filter(p => !isNaN(p) && p > 0);
    const avg = validPrices.length > 0 
      ? (validPrices.reduce((sum, p) => sum + p, 0) / validPrices.length).toFixed(1)
      : 'Liên hệ';
    
    const grades = filteredBuildings.map(b => (b.grade || 'C').toUpperCase()).filter(Boolean);
    const gradeCounts = grades.reduce((acc, g) => {
      acc[g] = (acc[g] || 0) + 1;
      return acc;
    }, {});
    
    return {
      total,
      avg: avg !== 'Liên hệ' ? `$${avg}/m²` : 'Liên hệ',
      gradeCounts
    };
  }, [filteredBuildings]);

  useSEO({
    title: stats 
      ? `Cho thuê văn phòng Phường ${cleanWardName} — ${stats.total} Tòa nhà giá từ ${stats.avg}`
      : `Cho thuê văn phòng Phường ${cleanWardName} — Danh sách cập nhật mới nhất`,
    description: stats
      ? `Hiện có ${stats.total} tòa nhà văn phòng cho thuê tại Phường ${cleanWardName}, Đà Nẵng. Mức giá trung bình đạt ${stats.avg}/tháng. Bản đồ & so sánh giá trực quan.`
      : `Danh sách các tòa nhà văn phòng cho thuê tại Phường ${cleanWardName}, Đà Nẵng. Đa dạng diện tích, giá tốt, hỗ trợ tư vấn miễn phí.`,
  });

  return (
    <main>
      <div className="breadcrumb-bar">
        <div className="container breadcrumb-list">
          <Link to="/">Trang chủ</Link>
          <span className="breadcrumb-sep">›</span>
          <Link to="/">Cho thuê văn phòng</Link>
          <span className="breadcrumb-sep">›</span>
          <span style={{textTransform: 'capitalize'}}>Phường {cleanWardName}</span>
        </div>
      </div>

      <div className="page-head" style={{ background: '#f8f9fa', borderBottom: '1px solid #eee', padding: '30px 0' }}>
        <div className="container">
          <h1 style={{ margin: '0 0 12px 0' }}>Cho thuê văn phòng Phường <span style={{textTransform: 'capitalize'}}>{cleanWardName}</span></h1>
          <p className="desc" style={{ maxWidth: '800px', margin: '0' }}>
            Tổng hợp danh sách các tòa nhà văn phòng cho thuê chuyên nghiệp tại Phường {cleanWardName}. 
            Với lợi thế vị trí đắc địa và nhiều tiện ích xung quanh, Phường {cleanWardName} là lựa chọn hàng đầu cho các doanh nghiệp đặt trụ sở làm việc.
          </p>

          {stats && (
            <div className="quick-stats-box" style={{ 
              display: 'flex', 
              flexWrap: 'wrap',
              gap: '24px', 
              marginTop: '20px', 
              background: '#fff', 
              padding: '16px 24px', 
              borderRadius: '8px', 
              border: '1px solid #eee', 
              boxShadow: '0 2px 8px rgba(0,0,0,0.03)',
              width: 'fit-content'
            }}>
              <div>
                <span style={{ display: 'block', fontSize: '0.85rem', color: '#666', marginBottom: '2px' }}>Tổng số tòa nhà</span>
                <strong style={{ fontSize: '1.2rem', color: '#2c3e50' }}>{stats.total} văn phòng</strong>
              </div>
              <div style={{ width: '1px', background: '#eee' }} className="stats-divider" />
              <div>
                <span style={{ display: 'block', fontSize: '0.85rem', color: '#666', marginBottom: '2px' }}>Giá thuê trung bình</span>
                <strong style={{ fontSize: '1.2rem', color: '#e31c5f' }}>{stats.avg}/tháng</strong>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="container" style={{ padding: '50px 15px' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '100px 20px' }}>
            <div style={{ fontSize: '2rem', animation: 'spin 1s infinite linear', display: 'inline-block', marginBottom: 16 }}>⏳</div>
            <p style={{ color: '#999' }}>Đang tải danh sách tòa nhà...</p>
          </div>
        ) : filteredBuildings.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 20px', background: '#fff', borderRadius: 12, border: '1px solid #eee' }}>
            <div style={{ fontSize: '3rem', marginBottom: 12 }}>🔍</div>
            <h3 style={{ marginBottom: 8 }}>Không có dữ liệu</h3>
            <p style={{ color: '#999', marginBottom: 20 }}>Hiện tại chưa có tòa nhà nào được cập nhật tại Phường {cleanWardName}.</p>
            <Link to="/" className="btn-view-all">Quay lại Trang chủ</Link>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '24px'
          }}>
            {filteredBuildings.map(b => (
              <BuildingCard building={b} key={b.id} />
            ))}
          </div>
        )}
      </div>

      <div style={{ padding: '60px 0', background: '#eef2f5' }}>
        <div className="container" style={{ maxWidth: 600 }}>
          <div style={{ textAlign: 'center', marginBottom: 30 }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--dark)' }}>Cần tư vấn văn phòng tại Phường {cleanWardName}?</h2>
            <p style={{ color: 'var(--text)' }}>Để lại thông tin, chuyên viên của chúng tôi sẽ liên hệ báo giá và hỗ trợ đi xem thực tế miễn phí.</p>
          </div>
          <ContactForm />
        </div>
      </div>
    </main>
  );
}
