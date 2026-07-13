import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Award, Layers, Maximize, Compass, ArrowUpDown, Clock, DollarSign, Briefcase, ParkingCircle, Zap, CreditCard, Calendar, Wallet, Moon } from 'lucide-react';
import { fetchBuildings } from '../utils/api';
import { useSEO } from '../utils/seo';
import ContactForm from '../components/ContactForm';
import BuildingCard from '../components/BuildingCard';
import Carousel from '../components/Carousel';
import { marked } from 'marked';

export default function BuildingPage() {
  const { slug } = useParams();
  const [b, setB] = useState(null);
  const [related, setRelated] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);
    document.body.classList.add('has-sticky-cta');
    fetchBuildings().then(data => {
      const found = data.find(x => x.id === slug);
      setB(found);
      if (found) {
        setRelated(data.filter(x => x.district === found.district && x.id !== slug).slice(0, 3));
      }
      setLoading(false);
    });
    return () => {
      document.body.classList.remove('has-sticky-cta');
    };
  }, [slug]);

  useSEO({
    title: b ? `${b.name} — Cho thuê văn phòng ${b.district}` : '',
    description: b ? `Cho thuê văn phòng tại ${b.name}, ${b.address}. Quy mô ${b.totalFloors} tầng, giá thuê từ $${b.price}/m2. Cập nhật diện tích trống mới nhất.` : '',
    schema: b ? {
      "@context": "https://schema.org",
      "@type": "Product",
      "name": b.name,
      "description": b.description,
      "offers": {
        "@type": "Offer",
        "price": b.price,
        "priceCurrency": "USD",
        "unitText": "per sqm per month"
      },
      "address": {
        "@type": "PostalAddress",
        "streetAddress": b.address,
        "addressLocality": "Đà Nẵng",
        "addressCountry": "VN"
      }
    } : null
  });

  if (loading) {
    return (
      <main>
        <div className="container" style={{ padding: '40px 0' }}>
          <div className="breadcrumb-bar" style={{ marginBottom: '16px' }}>
            <div style={{ height: '20px', width: '200px', borderRadius: '4px' }} className="skeleton" />
          </div>
          <div style={{ height: '40px', width: '40%', marginBottom: '12px', borderRadius: '4px' }} className="skeleton" />
          <div style={{ height: '20px', width: '60%', marginBottom: '24px', borderRadius: '4px' }} className="skeleton" />
          <div className="building-gallery-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '32px' }}>
            <div style={{ borderRadius: '8px', aspectRatio: '4/3' }} className="skeleton" />
            <div style={{ borderRadius: '8px', aspectRatio: '4/3' }} className="skeleton" />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '16px', marginBottom: '32px' }}>
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} style={{ height: '80px', borderRadius: '12px' }} className="skeleton" />
            ))}
          </div>
        </div>
      </main>
    );
  }

  if (!b) {
    return (
      <main>
        <div className="container" style={{ textAlign: 'center', padding: '80px 20px' }}>
          <div style={{ fontSize: '4rem', marginBottom: 16 }}>🏢</div>
          <h1 style={{ fontSize: '1.5rem', marginBottom: 12 }}>Tòa nhà không tồn tại</h1>
          <p style={{ color: '#999', marginBottom: 24 }}>Trang bạn tìm không tồn tại hoặc đã bị xóa.</p>
          <Link to="/" className="btn-view-all">← Quay lại trang chủ</Link>
        </div>
      </main>
    );
  }

  const specs = [
    ['Giá thuê', `$${b.price}/m²/tháng`, true],
    ['Phí dịch vụ', b.serviceCharge ? `$${b.serviceCharge}/m²/tháng` : 'Bao gồm trong giá thuê'],
    ['Hạng tòa nhà', `Hạng ${b.grade}`],
    ['Diện tích sàn', b.floorArea],
    ['Số tầng', `${b.totalFloors} tầng${b.basements ? ` + ${b.basements} hầm` : ''}`],
    ['Diện tích trống', b.availableAreas],
    ['Hướng', b.direction],
    ['Phí gửi xe', b.parkingFee],
    ['Tiền điện', b.electricityFee],
    ['Thời hạn thuê', b.leaseTerm],
    ['Đặt cọc', b.deposit],
    ['Thanh toán', b.payment],
  ];

  return (
    <main>
      <div className="container">
        <div className="breadcrumb-bar">
          <div className="breadcrumb-list">
            <Link to="/">Trang chủ</Link>
            <span className="breadcrumb-sep">›</span>
            <Link to="/">Cho thuê văn phòng Đà Nẵng</Link>
            <span className="breadcrumb-sep">›</span>
            <span>{b.name}</span>
          </div>
        </div>

        <div className="building-header" style={{ marginBottom: '24px', marginTop: '16px' }}>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: '#2c3e50', marginBottom: '12px' }}>{b.name}</h1>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <p style={{ fontSize: '1.05rem', color: '#666', margin: 0, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{color: '#e31c5f'}}>📍</span> {b.address}
            </p>
            <button style={{ background: 'none', border: 'none', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.95rem' }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg> Chia sẻ
            </button>
          </div>
        </div>

        <div className="building-gallery-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '32px' }}>
          {(() => {
            const images = b.gallery || [b.imageUrl || b.image];
            const img1 = images[0];
            const img2 = images.length > 1 ? images[1] : images[0];
            
            return (
              <>
                <div style={{ borderRadius: '8px', overflow: 'hidden', aspectRatio: '4/3', cursor: 'pointer', backgroundColor: '#f8fafc' }} onClick={() => setIsGalleryOpen(true)}>
                  <img src={img1} alt={`${b.name} 1`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                </div>
                <div style={{ borderRadius: '8px', overflow: 'hidden', aspectRatio: '4/3', position: 'relative', cursor: 'pointer', backgroundColor: '#f8fafc' }} onClick={() => setIsGalleryOpen(true)}>
                  <img src={img2} alt={`${b.name} 2`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  <button style={{ 
                    position: 'absolute', bottom: '24px', right: '24px', 
                    background: 'white', padding: '12px 28px', borderRadius: '4px', 
                    border: 'none', fontWeight: '700', cursor: 'pointer', 
                    boxShadow: '0 4px 12px rgba(0,0,0,0.15)', fontSize: '1rem',
                    color: '#333'
                  }} onClick={(e) => { e.stopPropagation(); setIsGalleryOpen(true); }}>
                    Xem thêm
                  </button>
                </div>
              </>
            );
          })()}
        </div>
      </div>

      <div className="js-navbar-detail-affix" style={{ position: 'sticky', top: 0, zIndex: 100, background: 'rgba(255, 255, 255, 0.85)', backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)', borderBottom: '1px solid rgba(0,0,0,0.05)', boxShadow: '0 4px 20px rgba(0, 0, 0, 0.03)' }}>
        <div className="detail-menu-sticky" style={{ padding: '16px 0' }}>
          <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <ul className="js-navbar-nav" style={{ display: 'flex', gap: '32px', listStyle: 'none', margin: 0, padding: 0, fontWeight: 600, fontSize: '1.05rem' }}>
              <li><a href="#thong_so" style={{ color: '#475569', textDecoration: 'none', transition: 'color 0.2s' }}>Thông số</a></li>
              <li><a href="#chi_tiet_gia" style={{ color: '#475569', textDecoration: 'none', transition: 'color 0.2s' }}>Chi tiết giá</a></li>
              <li><a href="#dien_tich" style={{ color: '#475569', textDecoration: 'none', transition: 'color 0.2s' }}>Diện tích</a></li>
              <li><a href="#tong_quan" style={{ color: '#475569', textDecoration: 'none', transition: 'color 0.2s' }}>Tổng quan</a></li>
              <li><a href="#dia_diem" style={{ color: '#475569', textDecoration: 'none', transition: 'color 0.2s' }}>Bản đồ</a></li>
            </ul>
            <div className="navbar-right" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <span className="price" style={{ fontWeight: 800, color: '#e31c5f', fontSize: '1.2rem' }}>
                {parseFloat(b.price) > 0 ? `$${parseFloat(b.price)} ${parseFloat(b.serviceCharge) > 0 ? `+ $${parseFloat(b.serviceCharge)} DV` : ''} /m²` : 'Liên hệ'}
              </span>
              <a className="btn btn-phone" href="tel:0987667270" style={{ background: 'linear-gradient(135deg, #e31c5f 0%, #ff4d4d 100%)', color: '#fff', padding: '10px 24px', borderRadius: '30px', fontWeight: 'bold', textDecoration: 'none', boxShadow: '0 4px 15px rgba(227, 28, 95, 0.3)', transition: 'transform 0.2s, box-shadow 0.2s' }}>Gọi ngay 098.766.7270</a>
            </div>
          </div>
        </div>
      </div>

      <div style={{ background: '#f5f5f5', padding: '30px 0' }}>
        <div className="container">
          <div className="detail-grid">
            <div className="detail-main building-content" style={{ padding: '20px', borderRadius: '4px', border: '1px solid #eee' }}>
              
              <div className="box-item tab-item" id="thong_so">
                <div className="tab-title" style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '20px', borderBottom: '1px solid #eee', paddingBottom: '12px' }}>Thông số toà nhà</div>
                <div className="tab-content" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '16px' }}>
                  
                  <div style={{ background: '#fff', border: '1px solid #f0f0f0', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                    <div style={{ background: '#fdf2f8', padding: '12px', borderRadius: '10px', color: '#e31c5f' }}><Award size={24} strokeWidth={1.5} /></div>
                    <div>
                      <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>Hạng tòa nhà</div>
                      <div style={{ fontWeight: 600, color: '#2c3e50', fontSize: '1.05rem' }}>Hạng {b.grade || 'C'}</div>
                    </div>
                  </div>

                  <div style={{ background: '#fff', border: '1px solid #f0f0f0', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                    <div style={{ background: '#f0fdf4', padding: '12px', borderRadius: '10px', color: '#16a34a' }}><Layers size={24} strokeWidth={1.5} /></div>
                    <div>
                      <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>Quy mô</div>
                      <div style={{ fontWeight: 600, color: '#2c3e50', fontSize: '1.05rem' }}>{b.totalFloors} tầng {b.basements ? `+ ${b.basements} hầm` : ''}</div>
                    </div>
                  </div>

                  <div style={{ background: '#fff', border: '1px solid #f0f0f0', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                    <div style={{ background: '#eff6ff', padding: '12px', borderRadius: '10px', color: '#2563eb' }}><Maximize size={24} strokeWidth={1.5} /></div>
                    <div>
                      <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>Diện tích sàn</div>
                      <div style={{ fontWeight: 600, color: '#2c3e50', fontSize: '1.05rem' }}>{b.floorArea || 'Đang cập nhật'}</div>
                    </div>
                  </div>

                  <div style={{ background: '#fff', border: '1px solid #f0f0f0', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                    <div style={{ background: '#fffbeb', padding: '12px', borderRadius: '10px', color: '#d97706' }}><Compass size={24} strokeWidth={1.5} /></div>
                    <div>
                      <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>Hướng</div>
                      <div style={{ fontWeight: 600, color: '#2c3e50', fontSize: '1.05rem' }}>{b.direction || 'Đang cập nhật'}</div>
                    </div>
                  </div>

                  <div style={{ background: '#fff', border: '1px solid #f0f0f0', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                    <div style={{ background: '#f5f3ff', padding: '12px', borderRadius: '10px', color: '#7c3aed' }}><ArrowUpDown size={24} strokeWidth={1.5} /></div>
                    <div>
                      <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>Thang máy</div>
                      <div style={{ fontWeight: 600, color: '#2c3e50', fontSize: '1.05rem' }}>Tốc độ cao</div>
                    </div>
                  </div>

                  <div style={{ background: '#fff', border: '1px solid #f0f0f0', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                    <div style={{ background: '#ecfdf5', padding: '12px', borderRadius: '10px', color: '#059669' }}><Clock size={24} strokeWidth={1.5} /></div>
                    <div>
                      <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>Giờ làm việc</div>
                      <div style={{ fontWeight: 600, color: '#2c3e50', fontSize: '1.05rem' }}>T2 - T6: 08:00 - 18:00<br/><span style={{fontSize: '0.9rem', color: '#64748b'}}>T7: 08:00 - 12:00</span></div>
                    </div>
                  </div>

                </div>
              </div>

              <div className="box-item tab-item" id="chi_tiet_gia" style={{ marginTop: '32px' }}>
                <div className="tab-title" style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '20px', borderBottom: '1px solid #eee', paddingBottom: '12px' }}>Giá, phí dịch vụ và chi phí khác</div>
                <div className="tab-content" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '16px' }}>
                  
                  <div style={{ background: '#fff', border: '1px solid #f0f0f0', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                    <div style={{ background: '#fdf2f8', padding: '12px', borderRadius: '10px', color: '#e31c5f' }}><DollarSign size={24} strokeWidth={1.5} /></div>
                    <div>
                      <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>Giá thuê</div>
                      <div style={{ fontWeight: 600, color: '#e31c5f', fontSize: '1.05rem' }}>{parseFloat(b.price) > 0 ? `$${b.price}/m²/tháng` : 'Liên hệ'}</div>
                    </div>
                  </div>

                  <div style={{ background: '#fff', border: '1px solid #f0f0f0', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                    <div style={{ background: '#eff6ff', padding: '12px', borderRadius: '10px', color: '#2563eb' }}><Briefcase size={24} strokeWidth={1.5} /></div>
                    <div>
                      <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>Phí dịch vụ</div>
                      <div style={{ fontWeight: 600, color: '#2c3e50', fontSize: '1.05rem' }}>{b.serviceCharge ? `$${b.serviceCharge}/m²/tháng` : 'Bao gồm trong giá'}</div>
                    </div>
                  </div>

                  <div style={{ background: '#fff', border: '1px solid #f0f0f0', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                    <div style={{ background: '#f0fdf4', padding: '12px', borderRadius: '10px', color: '#16a34a' }}><ParkingCircle size={24} strokeWidth={1.5} /></div>
                    <div>
                      <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>Đỗ xe máy</div>
                      <div style={{ fontWeight: 600, color: '#2c3e50', fontSize: '1.05rem' }}>{b.parkingFee || 'Đang cập nhật'}</div>
                    </div>
                  </div>

                  <div style={{ background: '#fff', border: '1px solid #f0f0f0', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                    <div style={{ background: '#fffbeb', padding: '12px', borderRadius: '10px', color: '#d97706' }}><Zap size={24} strokeWidth={1.5} /></div>
                    <div>
                      <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>Tiền điện</div>
                      <div style={{ fontWeight: 600, color: '#2c3e50', fontSize: '1.05rem' }}>{b.electricityFee || 'Đồng hồ riêng'}</div>
                    </div>
                  </div>

                  <div style={{ background: '#fff', border: '1px solid #f0f0f0', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                    <div style={{ background: '#f5f3ff', padding: '12px', borderRadius: '10px', color: '#7c3aed' }}><CreditCard size={24} strokeWidth={1.5} /></div>
                    <div>
                      <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>Thanh toán</div>
                      <div style={{ fontWeight: 600, color: '#2c3e50', fontSize: '1.05rem' }}>{b.payment || 'Theo quý/tháng'}</div>
                    </div>
                  </div>

                    <div style={{ background: '#fff', border: '1px solid #f0f0f0', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                      <div style={{ background: '#ecfdf5', padding: '12px', borderRadius: '10px', color: '#059669' }}><Calendar size={24} strokeWidth={1.5} /></div>
                      <div>
                        <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>Thời hạn thuê</div>
                        <div style={{ fontWeight: 600, color: '#2c3e50', fontSize: '1.05rem' }}>{b.leaseTerm || 'Tối thiểu 2 năm'}</div>
                      </div>
                    </div>

                    <div style={{ background: '#fff', border: '1px solid #f0f0f0', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                      <div style={{ background: '#fef3c7', padding: '12px', borderRadius: '10px', color: '#d97706' }}><Wallet size={24} strokeWidth={1.5} /></div>
                      <div>
                        <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>Đặt cọc</div>
                        <div style={{ fontWeight: 600, color: '#2c3e50', fontSize: '1.05rem' }}>{b.deposit || '3 tháng'}</div>
                      </div>
                    </div>

                    <div style={{ background: '#fff', border: '1px solid #f0f0f0', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                      <div style={{ background: '#f3e8ff', padding: '12px', borderRadius: '10px', color: '#9333ea' }}><Moon size={24} strokeWidth={1.5} /></div>
                      <div>
                        <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '4px' }}>Phí ngoài giờ</div>
                        <div style={{ fontWeight: 600, color: '#2c3e50', fontSize: '1.05rem' }}>{b.overtimeFee || 'Thương lượng'}</div>
                      </div>
                    </div>

                </div>
              </div>

              <div className="box-item tab-item" id="dien_tich">
                <div className="tab-title">Các diện tích còn trống</div>
                <div className="tab-content">
                  <table className="maison-table">
                    <thead>
                      <tr>
                        <th>Tầng</th>
                        <th>Diện tích (m2)</th>
                        <th>Giá thuê (Tháng)</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>Liên hệ</td>
                        <td>{b.availableAreas || 'Đang cập nhật'}</td>
                        <td><strong style={{color: '#e31c5f'}}>${b.price}/m2/tháng</strong></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="box-item tab-item" id="tong_quan">
                <div className="tab-title">Tổng quan tòa nhà {b.name}</div>
                <div className="tab-content">
                  <div className="modal-desc" dangerouslySetInnerHTML={{ __html: (() => {
                    let text = b.description || '';
                    return text;
                  })() }} style={{ color: '#333' }} />
                </div>
              </div>



            </div>

            <div className="detail-sidebar">
              <div className="detail-price-box" style={{ background: '#fff', border: '1px solid #ffe4e6', borderRadius: '12px', padding: '24px', marginBottom: '24px', boxShadow: '0 4px 20px rgba(227, 28, 95, 0.05)' }}>
                {parseFloat(b.price) > 0 ? (
                  <>
                    <div style={{ fontSize: '0.95rem', color: '#64748b', marginBottom: '8px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Tổng chi phí thuê</div>
                    <div style={{ color: '#e31c5f', fontSize: '2.2rem', fontWeight: 800, lineHeight: 1 }}>
                      ${parseFloat(b.price) + (parseFloat(b.serviceCharge) || 0)} <span style={{ fontSize: '1.1rem', fontWeight: 500, color: '#64748b' }}>/m²/tháng</span>
                    </div>
                    
                    <div style={{ marginTop: '20px', borderTop: '1px dashed #e2e8f0', paddingTop: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#475569', fontSize: '1.05rem' }}>
                        <span>Giá thuê cơ sở</span>
                        <strong style={{ color: '#1e293b' }}>${parseFloat(b.price)}/m²</strong>
                      </div>
                      {parseFloat(b.serviceCharge) > 0 ? (
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#475569', fontSize: '1.05rem' }}>
                          <span>Phí dịch vụ</span>
                          <strong style={{ color: '#1e293b' }}>${parseFloat(b.serviceCharge)}/m²</strong>
                        </div>
                      ) : (
                        <div style={{ color: '#64748b', fontSize: '0.9rem', fontStyle: 'italic', marginTop: '-4px', textAlign: 'left' }}>
                          * Phí dịch vụ đã bao gồm trong giá thuê
                        </div>
                      )}
                    </div>
                    <div style={{ color: '#64748b', fontSize: '0.9rem', fontStyle: 'italic', marginTop: '16px', textAlign: 'left' }}>
                      * Giá thuê trên chưa bao gồm VAT
                    </div>
                  </>
                ) : (
                  <div style={{ color: '#e31c5f', fontSize: '2rem', fontWeight: 800 }}>Liên hệ</div>
                )}
                
                <a href="tel:0987667270" className="btn-hotline" style={{ display: 'block', marginTop: '24px', background: 'linear-gradient(135deg, #e31c5f 0%, #ff4d4d 100%)', color: 'white', padding: '14px 24px', borderRadius: '8px', textAlign: 'center', fontWeight: 'bold', fontSize: '1.1rem', textDecoration: 'none', boxShadow: '0 4px 15px rgba(227, 28, 95, 0.3)', transition: 'transform 0.2s' }}>
                  📞 NHẬN BÁO GIÁ
                </a>
              </div>
              
              <div className="sidebar-form">
                <h3 style={{ marginBottom: '16px', fontSize: '1.2rem' }}>TƯ VẤN & BÁO GIÁ</h3>
                <ContactForm buildingName={b.name} />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div style={{ background: '#f8fafc', padding: '60px 0' }} id="dia_diem">
        <div className="container">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
            <div style={{ background: '#e0f2fe', padding: '10px', borderRadius: '10px', color: '#0284c7' }}>
              <Compass size={28} strokeWidth={2} />
            </div>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#1e293b', margin: 0 }}>Vị trí {b.name} trên bản đồ</h2>
          </div>
          
          <div style={{ padding: '16px', background: '#fff', borderRadius: '16px', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025)' }}>
            <div style={{ fontSize: '1rem', color: '#475569', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <strong>📍 Địa chỉ:</strong> {b.address.replace(/,\s*(Thành phố |TP\.?\s*)?Đà Nẵng/gi, '')}
            </div>
            <div style={{ width: '100%', height: '400px', borderRadius: '12px', overflow: 'hidden', border: '1px solid #e2e8f0' }}>
              <iframe 
                title={`Bản đồ vị trí ${b.name}`}
                width="100%" 
                height="100%" 
                frameBorder="0" 
                style={{border: 'none'}}
                referrerPolicy="no-referrer-when-downgrade" 
                src={`https://www.google.com/maps?q=${encodeURIComponent(b.name + ' ' + b.address)}&z=18&output=embed`} 
                allowFullScreen>
              </iframe>
            </div>
          </div>
        </div>
      </div>

      {related.length > 0 && (
        <div style={{ background: '#fff', padding: '40px 0' }}>
          <div className="container">
            <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '20px', borderBottom: '2px solid #e31c5f', paddingBottom: '10px', display: 'inline-block' }}>Tòa nhà cùng khu vực Phường {b.district}</h2>
            <Carousel>
              {related.map(r => <BuildingCard building={r} key={r.id} />)}
            </Carousel>
          </div>
        </div>
      )}

      {isGalleryOpen && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 9999, background: 'rgba(0,0,0,0.95)', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '20px', display: 'flex', justifyContent: 'flex-end' }}>
            <button onClick={() => setIsGalleryOpen(false)} style={{ background: 'none', border: 'none', color: 'white', fontSize: '2.5rem', cursor: 'pointer', lineHeight: 1 }}>&times;</button>
          </div>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', padding: '0 40px 40px' }}>
            <div style={{ width: '100%', maxWidth: '1200px', height: '100%', position: 'relative' }}>
              <Carousel>
                {(b.gallery || [b.imageUrl || b.image]).map((img, idx) => (
                  <div key={idx} style={{ flex: '0 0 100%', scrollSnapAlign: 'start', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <img src={img} alt={`${b.name} - ${idx}`} style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }} />
                  </div>
                ))}
              </Carousel>
            </div>
          </div>
        </div>
      )}

      {/* Mobile Sticky CTA */}
      <div className="mobile-sticky-cta">
        <a href="tel:0987667270" className="btn-hotline" style={{ background: 'linear-gradient(135deg, #e31c5f 0%, #ff4d4d 100%)', color: 'white', borderRadius: '8px', textAlign: 'center', fontWeight: 'bold', textDecoration: 'none', boxShadow: '0 4px 15px rgba(227, 28, 95, 0.3)' }}>
          📞 NHẬN BÁO GIÁ TRỰC TIẾP
        </a>
      </div>
    </main>
  );
}
