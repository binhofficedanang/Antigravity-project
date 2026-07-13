import React, { useState, useMemo, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { fetchBuildings } from '../utils/api';
import { useSEO } from '../utils/seo';
import SearchBar from '../components/SearchBar';
import BuildingCard from '../components/BuildingCard';
import MapView from '../components/MapView';

export default function SearchPage() {
  const [searchParams] = useSearchParams();
  
  const q = searchParams.get('q') || '';
  const district = searchParams.get('district') || '';
  const price = searchParams.get('price') ? Number(searchParams.get('price')) : 40;
  const grades = searchParams.get('grades') ? searchParams.get('grades').split(',') : ['A', 'B', 'C'];

  // State to pass to SearchBar (initialize from URL)
  const [searchText, setSearchText] = useState(q);
  const [activeDistrict, setActiveDistrict] = useState(district);
  const [priceMax, setPriceMax] = useState(price);
  const [selectedGrades, setSelectedGrades] = useState(grades);

  const [buildingsData, setBuildingsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('list');

  // Sync state if URL changes (e.g. user clicks back button)
  useEffect(() => {
    setSearchText(q);
    setActiveDistrict(district);
    setPriceMax(price);
    setSelectedGrades(grades);
    window.scrollTo(0, 0);
  }, [q, district, price, searchParams]);

  useEffect(() => {
    fetchBuildings().then(data => {
      setBuildingsData(data);
      setLoading(false);
    });
  }, []);

  useSEO({
    title: `Kết quả tìm kiếm văn phòng | Office43`,
    description: `Tìm kiếm văn phòng cho thuê tại Đà Nẵng với bộ lọc thông minh. Kết quả tìm kiếm chính xác nhất.`,
  });

  // Filter based on URL parameters directly
  const filtered = useMemo(() => {
    return buildingsData.filter(b => {
      if (q && !b.name.toLowerCase().includes(q.toLowerCase()) && !b.address.toLowerCase().includes(q.toLowerCase())) return false;
      if (district && b.district !== district && !b.address.includes(district)) return false;
      if (b.price > price) return false;
      if (!grades.includes(b.grade)) return false;
      return true;
    });
  }, [buildingsData, q, district, price, grades]);

  return (
    <>
      <SearchBar
        searchText={searchText} setSearchText={setSearchText}
        activeDistrict={activeDistrict} setActiveDistrict={setActiveDistrict}
        priceMax={priceMax} setPriceMax={setPriceMax}
        selectedGrades={selectedGrades} setSelectedGrades={setSelectedGrades}
      />

      <main style={{ minHeight: '60vh', padding: '40px 0', background: '#f5f5f5' }}>
        <div className="container">
          <div className="breadcrumb-bar" style={{ marginBottom: 20 }}>
            <div className="breadcrumb-list">
              <Link to="/">Trang chủ</Link>
              <span className="breadcrumb-sep">›</span>
              <span>Kết quả tìm kiếm</span>
            </div>
          </div>

          <div style={{ marginBottom: 32, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
            <div>
              <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>Kết quả tìm kiếm</h1>
              <p style={{ color: '#666', marginTop: 8 }}>
                Tìm thấy <strong>{filtered.length}</strong> tòa nhà phù hợp với tiêu chí của bạn.
              </p>
            </div>
            
            <div className="view-tabs" style={{ borderBottom: 'none', marginBottom: 0 }}>
              <button className={`view-tab ${viewMode === 'list' ? 'active' : ''}`} onClick={() => setViewMode('list')}><span>📋</span> Danh sách</button>
              <button className={`view-tab ${viewMode === 'map' ? 'active' : ''}`} onClick={() => setViewMode('map')}><span>🗺️</span> Bản đồ</button>
              <button className={`view-tab ${viewMode === 'radius' ? 'active' : ''}`} onClick={() => setViewMode('radius')}><span>📍</span> Bán kính</button>
            </div>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '100px 20px' }}>
              <div style={{ fontSize: '2rem', animation: 'spin 1s infinite linear', display: 'inline-block', marginBottom: 16 }}>⏳</div>
              <p style={{ color: '#999' }}>Đang tải danh sách tòa nhà...</p>
            </div>
          ) : (
            filtered.length > 0 ? (
              viewMode === 'map' || viewMode === 'radius' ? (
                <MapView 
                  buildings={filtered} 
                  isRadiusMode={viewMode === 'radius'} 
                />
              ) : (
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', 
                  gap: '24px' 
                }}>
                  {filtered.map(b => <BuildingCard building={b} key={b.id} />)}
                </div>
              )
            ) : (
              <div style={{ textAlign: 'center', padding: '60px 20px', background: '#fff', borderRadius: 12 }}>
                <div style={{ fontSize: '3rem', marginBottom: 12 }}>🔍</div>
                <h3 style={{ marginBottom: 8 }}>Không tìm thấy kết quả</h3>
                <p style={{ color: '#999', marginBottom: 20 }}>Thử điều chỉnh bộ lọc của bạn để có thêm kết quả.</p>
                <Link to="/" className="btn-view-all" style={{ display: 'inline-block', padding: '10px 20px', background: '#e31c5f', color: '#fff', borderRadius: 6, textDecoration: 'none', fontWeight: 600 }}>Về trang chủ</Link>
              </div>
            )
          )}
        </div>
      </main>
    </>
  );
}
