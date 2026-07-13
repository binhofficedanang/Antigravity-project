import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { fetchBuildings } from '../utils/api';
import { useSEO, generateLocalBusinessSchema, generateWebSiteSchema } from '../utils/seo';


import SearchBar from '../components/SearchBar';
import BuildingCard from '../components/BuildingCard';
import SkeletonCard from '../components/SkeletonCard';
import Carousel from '../components/Carousel';
import FAQ from '../components/FAQ';
import ContactForm from '../components/ContactForm';
import MapView from '../components/MapView';
import SpaceCalculator from '../components/SpaceCalculator';

// Dùng đúng chuỗi như trong DB (Hoà = U+00E0, không phải Hòa U+00F2)
const ALL_DISTRICTS = [
  'Phường Hải Châu',
  'Phường Hoà Cường',
  'Phường Thanh Khê',
  'Phường An Khê',
  'Phường An Hải',
  'Phường Sơn Trà',
  'Phường Ngũ Hành Sơn',
  'Phường Hoà Khánh',
  'Phường Hải Vân',
  'Phường Liên Chiểu',
  'Phường Cẩm Lệ',
  'Phường Hoà Xuân',
];

function wardSlug(ward) {
  return ward
    .toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '') // bỏ dấu
    .replace(/đ/g, 'd')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

const BLOG_POSTS = [
  { slug: 'cach-tim-van-phong-cho-thue', title: 'Cách tìm văn phòng cho thuê hiệu quả: Mọi thứ bạn cần biết', excerpt: 'Lựa chọn văn phòng phù hợp là bước quan trọng giúp doanh nghiệp tạo dựng môi trường làm việc hiệu quả và nâng cao hình ảnh thương hiệu...', image: '/assets/indochina_riverside.jpg' },
  { slug: 'tieu-chi-danh-gia-toa-nha', title: '30+ Tiêu Chí Đánh Giá Tòa Nhà & Văn Phòng Cho Thuê', excerpt: 'Đánh giá tòa nhà văn phòng trước khi thuê là bước quyết định đến hiệu quả vận hành, chi phí duy trì và hình ảnh thương hiệu...', image: '/assets/bach_dang_complex.jpg' },
  { slug: 'kinh-nghiem-dam-phan-gia', title: 'Kinh Nghiệm Đàm Phán Giá & Chi Phí Thuê Văn Phòng', excerpt: 'Kinh nghiệm 10+ năm tư vấn và hỗ trợ khách hàng thuê văn phòng tại Đà Nẵng giúp bạn đàm phán giá thuê hiệu quả nhất...', image: '/assets/g8_golden.jpg' },
];

function groupByDistrict(buildings) {
  const groups = {};
  buildings.forEach(b => {
    if (!groups[b.district]) groups[b.district] = [];
    groups[b.district].push(b);
  });
  return groups;
}

export default function HomePage() {
  const [searchText, setSearchText] = useState('');
  const [activeDistrict, setActiveDistrict] = useState(null);
  const [priceMax, setPriceMax] = useState(40);
  const [selectedGrades, setSelectedGrades] = useState(['A', 'B', 'C']);
  const [viewMode, setViewMode] = useState('list');
  const [tabToast, setTabToast] = useState(null);
  
  // State for data
  const [buildingsData, setBuildingsData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBuildings().then(data => {
      setBuildingsData(data);
      setLoading(false);
    });
  }, []);

  const handleComingSoon = useCallback((name) => {
    setTabToast(name);
    setTimeout(() => setTabToast(null), 2500);
  }, []);

  useSEO({
    title: 'Cho thuê văn phòng Đà Nẵng — Hạng A, B, C giá tốt nhất',
    description: 'Tìm thuê văn phòng tại Đà Nẵng hạng A, B, C. Bộ lọc thông minh theo quận, giá, hạng. 23+ tòa nhà cập nhật mới nhất. Liên hệ nhận báo giá miễn phí.',
    schema: [generateLocalBusinessSchema(), generateWebSiteSchema()]
  });

  const filtered = useMemo(() => {
    return buildingsData.filter(b => {
      if (searchText && !b.name.toLowerCase().includes(searchText.toLowerCase()) && !b.address.toLowerCase().includes(searchText.toLowerCase())) return false;
      if (activeDistrict && b.district !== activeDistrict) return false;
      if (b.price > priceMax) return false;
      if (!selectedGrades.includes(b.grade)) return false;
      return true;
    });
  }, [buildingsData, searchText, activeDistrict, priceMax, selectedGrades]);

  const grouped = groupByDistrict(filtered);

  return (
    <>
      <SearchBar
        searchText={searchText} setSearchText={setSearchText}
        activeDistrict={activeDistrict} setActiveDistrict={setActiveDistrict}
        priceMax={priceMax} setPriceMax={setPriceMax}
        selectedGrades={selectedGrades} setSelectedGrades={setSelectedGrades}
      />

      <main>
        <div className="container">
          <div className="breadcrumb-bar">
            <div className="breadcrumb-list">
              <Link to="/">Trang chủ</Link>
              <span className="breadcrumb-sep">›</span>
              <span>Cho thuê văn phòng Đà Nẵng</span>
            </div>
          </div>

          <div className="page-head">
            <h1>Cho thuê văn phòng Đà Nẵng</h1>
            <p className="desc">
              Tư vấn tìm thuê văn phòng tại Đà Nẵng chuyên nghiệp miễn phí, đáp ứng mọi nhu cầu doanh nghiệp.
              Với hơn {loading ? '...' : buildingsData.length}+ toà nhà văn phòng hạng A-B-C đa dạng diện tích. Liên hệ nhận báo giá ngay!
            </p>
          </div>

          <SpaceCalculator />

          <div className="view-tabs">
            <button className={`view-tab ${viewMode === 'list' ? 'active' : ''}`} onClick={() => setViewMode('list')}><span>📋</span> Danh sách</button>
            <button className={`view-tab ${viewMode === 'map' ? 'active' : ''}`} onClick={() => setViewMode('map')}><span>🗺️</span> Bản đồ</button>
            <button className={`view-tab ${viewMode === 'radius' ? 'active' : ''}`} onClick={() => setViewMode('radius')}><span>📍</span> Bán kính</button>
            <button className={`view-tab ${viewMode === 'heatmap' ? 'active' : ''}`} onClick={() => setViewMode('heatmap')}><span>🔥</span> Bản đồ nhiệt (Giá)</button>
          </div>

          <div className="district-pills">
            {ALL_DISTRICTS
              .filter(d => buildingsData.some(b => b.district === d))
              .sort((a, b) => {
                // Đẩy các phường ít tòa nhà ra cuối
                const countA = buildingsData.filter(b => b.district === a).length;
                const countB = buildingsData.filter(b => b.district === b.district && b.district === b).length;
                const ca = buildingsData.filter(x => x.district === a).length;
                const cb = buildingsData.filter(x => x.district === b).length;
                if (ca <= 1 && cb > 1) return 1;
                if (cb <= 1 && ca > 1) return -1;
                return 0;
              })
              .map(d => (
                <Link
                  key={d}
                  to={`/phuong/${wardSlug(d)}`}
                  className="district-pill"
                >
                  {d}
                </Link>
              ))
            }
          </div>
        </div> {/* Đóng thẻ container chính của phần trên */}

        <div className="container" style={{ padding: '40px 0' }}>
          {loading ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '24px' }}>
              {[1, 2, 3, 4, 5, 6, 7, 8].map(i => <SkeletonCard key={i} />)}
            </div>
          ) : (
            (() => {
              // Always show all wards that have buildings, or filter if searchText is used
              const displayWards = activeDistrict ? [activeDistrict] : ALL_DISTRICTS;
              
              const renderedWards = displayWards.map((ward) => {
                const wardBuildings = buildingsData.filter(b => 
                  (b.district === ward || b.address.includes(ward)) && 
                  (!searchText || b.name.toLowerCase().includes(searchText.toLowerCase()) || b.address.toLowerCase().includes(searchText.toLowerCase())) &&
                  b.price <= priceMax &&
                  selectedGrades.includes(b.grade)
                );

                // Ưu tiên hiển thị các tòa nhà theo yêu cầu của user
                const priorityKeywords = {
                  'Phường Hải Châu': ['luxury', 'shb', 'bạch đằng complex', 'phi long'],
                  'Phường Thanh Khê': ['summit', 'ttc', 'thành công', 'hanvico']
                };

                wardBuildings.sort((a, b) => {
                  const pList = priorityKeywords[ward] || [];
                  const getPriority = (name) => {
                    const lowerName = name.toLowerCase();
                    const index = pList.findIndex(k => lowerName.includes(k));
                    return index === -1 ? 999 : index;
                  };
                  return getPriority(a.name) - getPriority(b.name);
                });

                // Ẩn section trên trang chủ nếu phường có quá ít tòa nhà (< 2)
                // Người dùng vẫn có thể vào trang phường qua button
                if (wardBuildings.length === 0) return null;
                if (!searchText && !activeDistrict && wardBuildings.length < 2) return null;

                return (
                  <div className="ward-section" key={ward} id={`ward-${ward}`} style={{ marginBottom: '50px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid #eaeaea', paddingBottom: '10px' }}>
                      <h3 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#333', margin: 0 }}>
                        {ward}
                      </h3>
                      <Link to={`/phuong/${ward.toLowerCase().replace(/ /g, '-')}`} style={{ fontSize: '0.85rem', color: '#333', textDecoration: 'underline', fontWeight: 600 }}>
                        Xem thêm
                      </Link>
                    </div>
                    <div style={{ 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', 
                      gap: '24px' 
                    }}>
                      {wardBuildings.slice(0, 4).map(b => <BuildingCard building={b} key={b.id} />)}
                    </div>
                  </div>
                );
              });

              if (renderedWards.every(w => w === null)) {
                return (
                  <div style={{ textAlign: 'center', padding: '60px 20px', background: '#fff', borderRadius: 12 }}>
                    <div style={{ fontSize: '3rem', marginBottom: 12 }}>🔍</div>
                    <h3 style={{ marginBottom: 8 }}>Không tìm thấy kết quả</h3>
                    <p style={{ color: '#999', marginBottom: 20 }}>Thử điều chỉnh bộ lọc của bạn.</p>
                    <button className="btn-view-all" onClick={() => { setSearchText(''); setPriceMax(40); setSelectedGrades(['A','B','C']); }}>Xem tất cả</button>
                  </div>
                );
              }

              if (viewMode === 'map' || viewMode === 'radius' || viewMode === 'heatmap') {
                return (
                  <MapView 
                    buildings={filtered} 
                    isRadiusMode={viewMode === 'radius'} 
                    isHeatmapMode={viewMode === 'heatmap'}
                  />
                );
              }

              return renderedWards;
            })()
          )}
        </div>

        {/* Interactive Tools Section */}
        <div className="interactive-tools-section" style={{ padding: '60px 0', background: 'linear-gradient(135deg, #fff0f4 0%, #fdfbf7 100%)' }}>
          <div className="container">
            <div style={{ textAlign: 'center', marginBottom: '40px' }}>
              <h2 style={{ fontSize: '2.2rem', color: '#e63946', marginBottom: '12px' }}>🚀 Khám Phá Trải Nghiệm Mới</h2>
              <p style={{ color: '#555', fontSize: '1.1rem' }}>Công cụ độc quyền từ Office43 giúp bạn tìm kiếm không gian làm việc thú vị hơn bao giờ hết.</p>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px' }}>
              
              <Link to="/office-matchmaker" style={{ textDecoration: 'none', color: 'inherit' }}>
                <div style={{ background: 'white', padding: '40px 30px', borderRadius: '24px', textAlign: 'center', boxShadow: '0 10px 30px rgba(0,0,0,0.05)', transition: 'transform 0.3s', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }} onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-10px)'} onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
                  <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🤝</div>
                  <h3 style={{ fontSize: '1.5rem', marginBottom: '12px', color: '#333' }}>Office Matchmaker</h3>
                  <p style={{ color: '#666', marginBottom: '24px', lineHeight: '1.5', flexGrow: 1 }}>Phân tích nhu cầu doanh nghiệp qua 4 câu hỏi khảo sát nhanh để hệ thống AI đề xuất các văn phòng phù hợp nhất.</p>
                  <span className="btn-primary" style={{ display: 'inline-block' }}>Phân tích ngay</span>
                </div>
              </Link>
              
              <Link to="/phong-thuy-van-phong" style={{ textDecoration: 'none', color: 'inherit' }}>
                <div style={{ background: 'white', padding: '40px 30px', borderRadius: '24px', textAlign: 'center', boxShadow: '0 10px 30px rgba(0,0,0,0.05)', transition: 'transform 0.3s', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }} onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-10px)'} onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
                  <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🧭</div>
                  <h3 style={{ fontSize: '1.5rem', marginBottom: '12px', color: '#333' }}>La Bàn Phong Thủy</h3>
                  <p style={{ color: '#666', marginBottom: '24px', lineHeight: '1.5', flexGrow: 1 }}>Sếp mệnh gì? Hợp hướng nào? Màu nào hút lộc? Công cụ tính toán ngũ hành chuẩn xác giúp doanh nghiệp làm ăn phát đạt.</p>
                  <span className="btn-primary" style={{ display: 'inline-block' }}>Xem phong thủy</span>
                </div>
              </Link>

            </div>
          </div>
        </div>

        {/* Grade Classification */}
        <div className="grade-section">
          <div className="container">
            <h2>Phân hạng các tòa nhà văn phòng cho thuê tại Đà Nẵng</h2>
            <p className="desc">Phân loại thành hạng A, B, và C dựa trên vị trí, tiện ích, dịch vụ, chất lượng xây dựng và giá thuê.</p>
            <div className="grade-grid">
              {['A', 'B', 'C'].map(g => {
                const gradeImages = {
                  'A': '/assets/indochina_riverside.jpg',
                  'B': '/assets/bach_dang_complex.jpg',
                  'C': '/assets/modern_office_generic.jpg'
                };
                return (
                  <Link to={`/tim-kiem?grades=${g}`} className="grade-card" key={g}>
                    <div className="grade-card-img"><img src={gradeImages[g]} alt={`Văn phòng hạng ${g}`} /></div>
                    <h3>Tòa nhà hạng {g} tại Đà Nẵng</h3>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>

        {/* Blog */}
        <div className="blog-section" id="blog-section">
          <div className="container">
            <h3 className="section-title">Kinh nghiệm thuê văn phòng</h3>
            <div className="blog-grid">
              {BLOG_POSTS.map((post, i) => (
                <Link to={`/blog/${post.slug}`} className="blog-card" key={i}>
                  <div className="blog-card-img"><img src={post.image} alt={post.title} loading="lazy" /></div>
                  <div className="blog-card-body">
                    <h4>{post.title}</h4>
                    <p className="excerpt">{post.excerpt}</p>
                  </div>
                </Link>
              ))}
            </div>
            <div className="text-center"><Link to="/blog" className="btn-view-all">Xem tất cả</Link></div>
          </div>
        </div>

        <FAQ />

        {/* Bottom contact */}
        <div style={{ padding: '40px 0' }} id="contact-section">
          <div className="container" style={{ maxWidth: 600 }}>
            <ContactForm />
          </div>
        </div>
      </main>
    </>
  );
}
