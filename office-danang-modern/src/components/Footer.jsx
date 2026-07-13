import React from 'react';
import { Link } from 'react-router-dom';

const ALL_DISTRICTS = ['Hải Châu', 'Thanh Khê', 'Sơn Trà', 'Cẩm Lệ', 'Ngũ Hành Sơn', 'Liên Chiểu'];

export default function Footer({ onFilterDistrict, onFilterGrade }) {
  return (
    <footer className="site-footer">
      <div className="container">
        <div className="footer-grid">
          <div className="footer-col brand">
            <h4>Office43</h4>
            <p>Trang thông tin thuê văn phòng chuyên nghiệp tại Đà Nẵng. Trải nghiệm tìm kiếm hiện đại, minh bạch, hiệu quả cho startup và doanh nghiệp.</p>
            <p style={{ fontSize: '0.75rem', color: '#555a6e', marginTop: 8 }}>Hệ thống thông tin văn phòng thuộc Office43.vn</p>
          </div>
          <div className="footer-col">
            <h4>Khu vực</h4>
            <div className="footer-links">
              {ALL_DISTRICTS.map(d => (
                <Link key={d} to={`/quan/${d.toLowerCase().replace(/\s+/g, '-').normalize('NFD').replace(/[\u0300-\u036f]/g, '')}`}>
                  Văn phòng {d}
                </Link>
              ))}
            </div>
          </div>
          <div className="footer-col">
            <h4>Phân hạng</h4>
            <div className="footer-links">
              <Link to="/hang/a">Tòa nhà Hạng A</Link>
              <Link to="/hang/b">Tòa nhà Hạng B</Link>
              <Link to="/hang/c">Tòa nhà Hạng C</Link>
              <Link to="/blog">Kinh nghiệm thuê</Link>
            </div>
          </div>
          <div className="footer-col">
            <h4>Liên hệ</h4>
            <div className="footer-links">
              <a href="tel:0987667270">📞 Hotline: 0987 667 270</a>
              <a href="https://zalo.me/0987667270" target="_blank" rel="noreferrer">💬 Chat Zalo: 0987 667 270</a>
              <a href="#">📍 Hải Châu, Đà Nẵng</a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          © {new Date().getFullYear()} Office43 — Cho thuê văn phòng Đà Nẵng uy tín
        </div>
      </div>
    </footer>
  );
}
