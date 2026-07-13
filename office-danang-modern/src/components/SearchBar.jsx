import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const ALL_DISTRICTS = ['Phường Hải Châu', 'Phường Hòa Cường', 'Phường Thanh Khê', 'Phường An Hải', 'Phường Liên Chiểu', 'Phường Cẩm Lệ', 'Phường Sơn Trà', 'Phường Hòa Xuân'];
const ALL_GRADES = ['A', 'B', 'C'];

export default function SearchBar({ searchText, setSearchText, activeDistrict, setActiveDistrict, priceMax, setPriceMax, selectedGrades, setSelectedGrades }) {
  const [openDropdown, setOpenDropdown] = useState(null);
  const [districtSearch, setDistrictSearch] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const ref = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpenDropdown(null);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const toggleGrade = (g) => {
    setSelectedGrades(prev => prev.includes(g) ? prev.filter(x => x !== g) : [...prev, g]);
  };

  const filteredDistricts = ALL_DISTRICTS.filter(d => d.toLowerCase().includes(districtSearch.toLowerCase()));

  const handleSearch = () => {
    setOpenDropdown(null);
    const params = new URLSearchParams();
    if (searchText) params.set('q', searchText);
    if (activeDistrict) params.set('district', activeDistrict);
    if (priceMax < 40) params.set('price', priceMax);
    if (selectedGrades.length > 0 && selectedGrades.length < 3) {
      params.set('grades', selectedGrades.join(','));
    }
    
    navigate(`/tim-kiem?${params.toString()}`);
  };

  return (
    <section className="search-bar-section" ref={ref}>
      <div className="container">
        <div className="search-bar">
          {/* Name search */}
          <div className="search-field name-field">
            <input
              className="search-name-input"
              type="text"
              placeholder="Tìm theo tên tòa nhà, tên đường hoặc địa chỉ"
              value={searchText}
              onChange={e => setSearchText(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
            />
          </div>

          {/* District */}
          <div className="search-field" style={{ position: 'relative' }}>
            <button className="search-field-btn" onClick={() => setOpenDropdown(openDropdown === 'district' ? null : 'district')}>
              <span className="search-field-label">Khu vực</span>
              <span className="search-field-value">{activeDistrict || '- Lựa chọn -'}</span>
            </button>
            {openDropdown === 'district' && (
              <div className="filter-dropdown">
                <div className="filter-dropdown-title">Chọn Phường / Khu vực</div>
                <input className="filter-search-inside" placeholder="Lọc Phường / Khu vực" value={districtSearch} onChange={e => setDistrictSearch(e.target.value)} />
                <div className="district-list-dropdown">
                  {filteredDistricts.map(d => (
                    <div key={d} className={`district-option ${activeDistrict === d ? 'selected' : ''}`}
                      onClick={() => { setActiveDistrict(activeDistrict === d ? null : d); setOpenDropdown(null); setDistrictSearch(''); }}>
                      {d}
                    </div>
                  ))}
                </div>
                <div className="filter-actions">
                  <button className="btn-filter-reset" onClick={() => { setActiveDistrict(null); setOpenDropdown(null); }}>Đặt lại</button>
                  <button className="btn-filter-save" onClick={() => setOpenDropdown(null)}>Lưu</button>
                </div>
              </div>
            )}
          </div>

          {/* Price */}
          <div className="search-field" style={{ position: 'relative' }}>
            <button className="search-field-btn" onClick={() => setOpenDropdown(openDropdown === 'price' ? null : 'price')}>
              <span className="search-field-label">Giá</span>
              <span className="search-field-value">$0 - ${priceMax}</span>
            </button>
            {openDropdown === 'price' && (
              <div className="filter-dropdown">
                <div className="filter-dropdown-title">Chọn khoảng giá</div>
                <div className="price-slider-area">
                  <div className="price-range-display">
                    <input type="text" className="price-box" value="$0" readOnly />
                    <span className="price-sep">—</span>
                    <input type="text" className="price-box" value={`$${priceMax}`} readOnly />
                  </div>
                  <input type="range" min="5" max="40" step="1" value={priceMax} onChange={e => setPriceMax(Number(e.target.value))} />
                </div>
                <div className="filter-actions">
                  <button className="btn-filter-reset" onClick={() => setPriceMax(40)}>Đặt lại</button>
                  <button className="btn-filter-save" onClick={() => setOpenDropdown(null)}>Lưu</button>
                </div>
              </div>
            )}
          </div>

          {/* Grade */}
          <div className="search-field" style={{ position: 'relative' }}>
            <button className="search-field-btn" onClick={() => setOpenDropdown(openDropdown === 'grade' ? null : 'grade')}>
              <span className="search-field-label">Hạng</span>
              <span className="search-field-value">{selectedGrades.length === 3 ? 'Tất cả' : selectedGrades.map(g => `Hạng ${g}`).join(', ') || '- Chọn -'}</span>
            </button>
            {openDropdown === 'grade' && (
              <div className="filter-dropdown">
                <div className="filter-dropdown-title">Chọn hạng</div>
                <div className="grade-checkbox-list">
                  <label className="grade-check-item">
                    <input type="checkbox" checked={selectedGrades.length === 3} onChange={() => setSelectedGrades(selectedGrades.length === 3 ? [] : ['A','B','C'])} />
                    Tất cả
                  </label>
                  {ALL_GRADES.map(g => (
                    <label key={g} className="grade-check-item">
                      <input type="checkbox" checked={selectedGrades.includes(g)} onChange={() => toggleGrade(g)} />
                      Hạng {g}
                    </label>
                  ))}
                </div>
                <div className="filter-actions">
                  <button className="btn-filter-reset" onClick={() => setSelectedGrades(['A','B','C'])}>Đặt lại</button>
                  <button className="btn-filter-save" onClick={() => setOpenDropdown(null)}>Lưu</button>
                </div>
              </div>
            )}
          </div>

          <button className="btn-search" onClick={handleSearch}>Tìm kiếm</button>
        </div>
      </div>
    </section>
  );
}
