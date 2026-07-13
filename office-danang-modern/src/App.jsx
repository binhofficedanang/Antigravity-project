import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';

import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import BuildingPage from './pages/BuildingPage';
import BlogPage from './pages/BlogPage';
import WardPage from './pages/WardPage';
import SearchPage from './pages/SearchPage';
import AdminMap from './pages/AdminMap';
import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';
import CompareTool from './components/CompareTool';
import { CompareProvider } from './context/CompareContext';
import MatchmakerPage from './pages/MatchmakerPage';
import FengShuiPage from './pages/FengShuiPage';

function ScrollToTop() {
  // Scroll to top on route change
  React.useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  return null;
}

function App() {
  return (
    <CompareProvider>
      <BrowserRouter>
        <Header />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/tim-kiem" element={<SearchPage />} />
          <Route path="/van-phong/:slug" element={<BuildingPage />} />
          <Route path="/blog" element={<BlogPage />} />
          <Route path="/blog/:slug" element={<BlogPage />} />
          <Route path="/phong-thuy-van-phong" element={<FengShuiPage />} />
          <Route path="/office-matchmaker" element={<MatchmakerPage />} />
          <Route path="/admin-map" element={<AdminMap />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route path="/phuong/:wardName" element={<WardPage />} />
          {/* 404 fallback */}
          <Route path="*" element={
            <main>
              <div className="container" style={{ textAlign: 'center', padding: '80px 20px' }}>
                <div style={{ fontSize: '4rem', marginBottom: 16 }}>404</div>
                <h1 style={{ marginBottom: 12 }}>Trang không tồn tại</h1>
                <p style={{ color: '#999', marginBottom: 24 }}>Trang bạn tìm không tồn tại hoặc đã được di chuyển.</p>
                <a href="/" className="btn-view-all">← Về trang chủ</a>
              </div>
            </main>
          } />
        </Routes>
        <CompareTool />
        <Footer />
      </BrowserRouter>
    </CompareProvider>
  );
}

export default App;
