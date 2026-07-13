import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

export default function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const scrollToSection = (e, sectionId) => {
    e.preventDefault();
    setMobileOpen(false);
    if (location.pathname !== '/') {
      navigate('/');
      // Wait for navigation then scroll
      setTimeout(() => {
        const el = document.getElementById(sectionId);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } else {
      const el = document.getElementById(sectionId);
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="site-header">
      <div className="container header-inner">
        <Link to="/" className="logo" onClick={() => setMobileOpen(false)}>
          <img src="/assets/logo.jpg" alt="Office43 Logo" style={{ height: '54px', width: 'auto', borderRadius: '4px', mixBlendMode: 'multiply' }} />
          <span style={{ marginLeft: '4px' }}>Office<span style={{color: 'var(--primary)'}}>43</span></span>
        </Link>
        <nav className={`header-nav ${mobileOpen ? 'open' : ''}`}>
          <Link to="/" onClick={() => setMobileOpen(false)} className={location.pathname === '/' ? 'active' : ''}>Cho thuê văn phòng</Link>
          <div className="header-dropdown">
            <span className={`dropdown-trigger ${(location.pathname === '/phong-thuy-van-phong' || location.pathname === '/office-matchmaker') ? 'active' : ''}`}>🚀 Trải Nghiệm ▾</span>
            <div className="dropdown-menu">
              <Link to="/office-matchmaker" onClick={() => setMobileOpen(false)}>🤝 Office Matchmaker</Link>
              <Link to="/phong-thuy-van-phong" onClick={() => setMobileOpen(false)}>🧭 La Bàn Phong Thủy</Link>
            </div>
          </div>
          <Link to="/blog" onClick={() => setMobileOpen(false)} className={location.pathname.startsWith('/blog') ? 'active' : ''}>Kinh nghiệm thuê</Link>
          <a href="#faq-section" onClick={(e) => scrollToSection(e, 'faq-section')}>Câu hỏi thường gặp</a>
          <a href="#contact-section" onClick={(e) => scrollToSection(e, 'contact-section')}>Liên hệ</a>
        </nav>
        <a href="tel:0987667270" className="btn-hotline">📞 0987 667 270</a>
        <button className="mobile-menu-btn" onClick={() => setMobileOpen(!mobileOpen)} aria-label="Menu">
          {mobileOpen ? '✕' : '☰'}
        </button>
      </div>
    </header>
  );
}
