import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../utils/api';

const ALL_DISTRICTS = ['Hải Châu', 'Thanh Khê', 'Sơn Trà', 'Cẩm Lệ', 'Ngũ Hành Sơn', 'Liên Chiểu'];
const ALL_GRADES = ['A', 'B', 'C'];

export default function AdminDashboard() {
  const [session, setSession] = useState(null);
  const [activeTab, setActiveTab] = useState('leads');
  const [leads, setLeads] = useState([]);
  const [buildings, setBuildings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingBuilding, setEditingBuilding] = useState(null); // holds building data if editing or empty object if adding
  const [formError, setFormError] = useState(null);
  const [formSaving, setFormSaving] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Auth Check
    supabase.auth.getSession().then(({ data: { session: currentSession } }) => {
      if (!currentSession) {
        navigate('/admin/login');
      } else {
        setSession(currentSession);
        loadData();
      }
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!session) {
        navigate('/admin/login');
      } else {
        setSession(session);
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load Leads
      const { data: leadsData, error: leadsError } = await supabase
        .from('leads')
        .select('*')
        .order('created_at', { ascending: false });
      
      if (leadsError) throw leadsError;
      setLeads(leadsData || []);

      // Load Buildings
      const { data: buildingsData, error: bldError } = await supabase
        .from('buildings')
        .select('*')
        .order('name', { ascending: true });

      if (bldError) throw bldError;
      setBuildings(buildingsData || []);
    } catch (err) {
      console.error('Error loading admin data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/admin/login');
  };

  const handleDeleteLead = async (id) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa thông tin liên hệ này?')) return;
    try {
      const { error } = await supabase.from('leads').delete().eq('id', id);
      if (error) throw error;
      setLeads(prev => prev.filter(x => x.id !== id));
    } catch (err) {
      alert('Không thể xóa lead: ' + err.message);
    }
  };

  const handleDeleteBuilding = async (id) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa tòa nhà này khỏi danh sách?')) return;
    try {
      const { error } = await supabase.from('buildings').delete().eq('id', id);
      if (error) throw error;
      setBuildings(prev => prev.filter(x => x.id !== id));
    } catch (err) {
      alert('Không thể xóa tòa nhà: ' + err.message);
    }
  };

  const handleSaveBuilding = async (e) => {
    e.preventDefault();
    setFormSaving(true);
    setFormError(null);

    const b = editingBuilding;
    if (!b.id || !b.name) {
      setFormError('ID (Slug) và Tên tòa nhà là bắt buộc.');
      setFormSaving(false);
      return;
    }

    try {
      const { error } = await supabase
        .from('buildings')
        .upsert({
          id: b.id.trim(),
          name: b.name.trim(),
          address: b.address || '',
          district: b.district || 'Hải Châu',
          price: String(b.price || ''),
          serviceCharge: String(b.serviceCharge || ''),
          parkingFee: b.parkingFee || '',
          electricityFee: b.electricityFee || '',
          overtimeFee: b.overtimeFee || '', // the new field!
          grade: b.grade || 'C',
          floorArea: b.floorArea || '',
          totalFloors: String(b.totalFloors || ''),
          basements: String(b.basements || ''),
          availableAreas: b.availableAreas || '',
          direction: b.direction || '',
          leaseTerm: b.leaseTerm || '',
          deposit: b.deposit || '',
          payment: b.payment || '',
          imageUrl: b.imageUrl || '',
          description: b.description || ''
        });

      if (error) throw error;

      setEditingBuilding(null);
      loadData();
      alert('Đã lưu thông tin tòa nhà thành công!');
    } catch (err) {
      console.error('Save error:', err);
      setFormError(err.message || 'Lỗi khi lưu dữ liệu.');
    } finally {
      setFormSaving(false);
    }
  };

  if (!session) return null;

  return (
    <main style={{ minHeight: '90vh', background: '#f8fafc', padding: '40px 0' }}>
      <div className="container" style={{ maxWidth: '1200px' }}>
        
        {/* Header Dashboard */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px', marginBottom: '32px', borderBottom: '1px solid #e2e8f0', paddingBottom: '20px' }}>
          <div>
            <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span>⚙️</span> CMS Admin Dashboard
            </h1>
            <p style={{ color: '#64748b', marginTop: '6px' }}>Quản lý dữ liệu văn phòng cho thuê Đà Nẵng</p>
          </div>
          <button 
            onClick={handleLogout}
            style={{ padding: '8px 18px', background: '#fff', border: '1px solid #cbd5e1', borderRadius: '6px', fontWeight: 600, color: '#b91c1c', cursor: 'pointer' }}
          >
            Đăng xuất 
          </button>
        </div>

        {/* Tab Controls / View Toggle */}
        <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
          <button 
            onClick={() => { setActiveTab('leads'); setEditingBuilding(null); }}
            style={{ 
              padding: '10px 24px', 
              borderRadius: '30px', 
              border: 'none', 
              fontWeight: 700, 
              cursor: 'pointer',
              background: activeTab === 'leads' ? '#e31c5f' : '#fff',
              color: activeTab === 'leads' ? '#fff' : '#64748b',
              boxShadow: '0 2px 4px rgba(0,0,0,0.02)'
            }}
          >
            📋 Khách Hàng Liên Hệ ({leads.length})
          </button>
          <button 
            onClick={() => { setActiveTab('buildings'); setEditingBuilding(null); }}
            style={{ 
              padding: '10px 24px', 
              borderRadius: '30px', 
              border: 'none', 
              fontWeight: 700, 
              cursor: 'pointer',
              background: activeTab === 'buildings' ? '#e31c5f' : '#fff',
              color: activeTab === 'buildings' ? '#fff' : '#64748b',
              boxShadow: '0 2px 4px rgba(0,0,0,0.02)'
            }}
          >
            🏢 Danh Sách Tòa Nhà ({buildings.length})
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '80px 20px' }}>
            <p style={{ color: '#64748b' }}>Đang tải dữ liệu admin...</p>
          </div>
        ) : editingBuilding ? (
          
          /* ========================================================
             FORM: ADD / EDIT BUILDING
             ======================================================== */
          <div style={{ background: '#fff', padding: '32px', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 15px rgba(0,0,0,0.02)' }}>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '24px', color: '#1e293b' }}>
              {editingBuilding.name ? `Sửa tòa nhà: ${editingBuilding.name}` : 'Thêm Tòa Nhà Mới'}
            </h2>

            {formError && (
              <div style={{ background: '#fef2f2', border: '1px solid #fca5a5', color: '#b91c1c', padding: '12px', borderRadius: '6px', marginBottom: '20px', fontSize: '0.85rem' }}>
                ⚠️ {formError}
              </div>
            )}

            <form onSubmit={handleSaveBuilding}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Mã định danh URL / Slug (Viết liền không dấu, vd: `toa-nha-ttc-plaza`)*</label>
                  <input
                    type="text"
                    required
                    disabled={!!editingBuilding.created_at} // disable editing slug once created
                    value={editingBuilding.id || ''}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, id: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Tên tòa nhà*</label>
                  <input
                    type="text"
                    required
                    value={editingBuilding.name || ''}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, name: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Địa chỉ*</label>
                  <input
                    type="text"
                    required
                    value={editingBuilding.address || ''}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, address: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Khu vực / Phường*</label>
                  <select
                    value={editingBuilding.district || 'Hải Châu'}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, district: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  >
                    {ALL_DISTRICTS.map(d => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '20px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Giá thuê ($/m2)*</label>
                  <input
                    type="text"
                    required
                    placeholder="12.5"
                    value={editingBuilding.price || ''}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, price: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Phí dịch vụ ($/m2)</label>
                  <input
                    type="text"
                    placeholder="2.5"
                    value={editingBuilding.serviceCharge || ''}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, serviceCharge: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Xếp hạng*</label>
                  <select
                    value={editingBuilding.grade || 'C'}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, grade: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  >
                    {ALL_GRADES.map(g => (
                      <option key={g} value={g}>Hạng {g}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Phí ngoài giờ (overtimeFee)</label>
                  <input
                    type="text"
                    placeholder="Miễn phí hoặc $0.05/m2/h"
                    value={editingBuilding.overtimeFee || ''}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, overtimeFee: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '20px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Số tầng nổi</label>
                  <input
                    type="text"
                    placeholder="12"
                    value={editingBuilding.totalFloors || ''}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, totalFloors: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Số tầng hầm</label>
                  <input
                    type="text"
                    placeholder="2"
                    value={editingBuilding.basements || ''}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, basements: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Tổng diện tích sàn</label>
                  <input
                    type="text"
                    placeholder="450 m2"
                    value={editingBuilding.floorArea || ''}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, floorArea: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Diện tích trống hiện tại</label>
                  <input
                    type="text"
                    placeholder="100m2, 230m2"
                    value={editingBuilding.availableAreas || ''}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, availableAreas: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '20px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Phí gửi xe</label>
                  <input
                    type="text"
                    placeholder="Xe máy: 100k, Ô tô: 1tr"
                    value={editingBuilding.parkingFee || ''}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, parkingFee: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Tiền điện</label>
                  <input
                    type="text"
                    placeholder="3.800đ/kwh"
                    value={editingBuilding.electricityFee || ''}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, electricityFee: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Thời hạn thuê</label>
                  <input
                    type="text"
                    placeholder="Tối thiểu 2 năm"
                    value={editingBuilding.leaseTerm || ''}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, leaseTerm: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Đặt cọc / Thanh toán</label>
                  <input
                    type="text"
                    placeholder="Cọc 3 tháng, trả 3 tháng"
                    value={editingBuilding.deposit || ''}
                    onChange={(e) => setEditingBuilding(prev => ({ ...prev, deposit: e.target.value }))}
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                  />
                </div>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Link ảnh đại diện (imageUrl)</label>
                <input
                  type="text"
                  placeholder="https://example.com/image.jpg"
                  value={editingBuilding.imageUrl || ''}
                  onChange={(e) => setEditingBuilding(prev => ({ ...prev, imageUrl: e.target.value }))}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                />
              </div>

              <div style={{ marginBottom: '28px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#475569', marginBottom: '6px' }}>Mô tả chi tiết (Hỗ trợ định dạng HTML)</label>
                <textarea
                  rows="6"
                  value={editingBuilding.description || ''}
                  onChange={(e) => setEditingBuilding(prev => ({ ...prev, description: e.target.value }))}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', outline: 'none' }}
                />
              </div>

              <div style={{ display: 'flex', gap: '16px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setEditingBuilding(null)}
                  style={{ padding: '12px 24px', background: '#f1f5f9', border: 'none', borderRadius: '6px', fontWeight: 600, color: '#475569', cursor: 'pointer' }}
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  disabled={formSaving}
                  style={{ padding: '12px 32px', background: '#e31c5f', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 700, cursor: 'pointer', opacity: formSaving ? 0.7 : 1 }}
                >
                  {formSaving ? 'Đang lưu...' : 'Lưu lại'}
                </button>
              </div>
            </form>
          </div>
        ) : activeTab === 'leads' ? (
          
          /* ========================================================
             TAB 1: LEADS LISTING
             ======================================================== */
          <div style={{ background: '#fff', borderRadius: '12px', border: '1px solid #e2e8f0', overflow: 'hidden', boxShadow: '0 4px 15px rgba(0,0,0,0.02)' }}>
            <div style={{ padding: '20px 24px', borderBottom: '1px solid #e2e8f0' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#1e293b' }}>Danh Sách Yêu Cầu Liên Hệ</h2>
            </div>
            
            {leads.length === 0 ? (
              <div style={{ padding: '60px 20px', textAlign: 'center', color: '#64748b' }}>
                <span style={{ fontSize: '2.5rem' }}>📭</span>
                <p style={{ marginTop: '12px' }}>Chưa có yêu cầu liên hệ nào được gửi.</p>
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                  <thead>
                    <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#475569', fontWeight: 700 }}>
                      <th style={{ padding: '16px' }}>Thời gian</th>
                      <th style={{ padding: '16px' }}>Khách hàng</th>
                      <th style={{ padding: '16px' }}>Liên hệ</th>
                      <th style={{ padding: '16px' }}>Tòa nhà quan tâm</th>
                      <th style={{ padding: '16px' }}>Ghi chú</th>
                      <th style={{ padding: '16px', textAlign: 'center' }}>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leads.map(lead => (
                      <tr key={lead.id} style={{ borderBottom: '1px solid #e2e8f0', verticalAlign: 'top' }}>
                        <td style={{ padding: '16px', color: '#64748b' }}>
                          {new Date(lead.created_at).toLocaleString('vi-VN')}
                        </td>
                        <td style={{ padding: '16px', fontWeight: 700, color: '#0f172a' }}>
                          {lead.name}
                        </td>
                        <td style={{ padding: '16px' }}>
                          <a href={`tel:${lead.phone}`} style={{ display: 'block', color: '#e31c5f', fontWeight: 600, textDecoration: 'none' }}>📞 {lead.phone}</a>
                          {lead.email && <span style={{ fontSize: '0.8rem', color: '#64748b' }}>✉️ {lead.email}</span>}
                        </td>
                        <td style={{ padding: '16px' }}>
                          <span style={{ fontWeight: 600, color: '#334155' }}>{lead.building_name}</span>
                          {lead.url && (
                            <a href={lead.url} target="_blank" rel="noreferrer" style={{ display: 'block', fontSize: '0.75rem', color: '#2563eb', textDecoration: 'underline', marginTop: '4px' }}>
                              Xem link nguồn
                            </a>
                          )}
                        </td>
                        <td style={{ padding: '16px', color: '#475569', maxWidth: '300px', wordBreak: 'break-word' }}>
                          {lead.note || '-'}
                        </td>
                        <td style={{ padding: '16px', textAlign: 'center' }}>
                          <button 
                            onClick={() => handleDeleteLead(lead.id)}
                            style={{ padding: '4px 10px', background: '#fef2f2', border: '1px solid #fee2e2', borderRadius: '4px', color: '#b91c1c', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}
                          >
                            Xóa
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ) : (
          
          /* ========================================================
             TAB 2: BUILDINGS MANAGEMENT
             ======================================================== */
          <div style={{ background: '#fff', borderRadius: '12px', border: '1px solid #e2e8f0', overflow: 'hidden', boxShadow: '0 4px 15px rgba(0,0,0,0.02)' }}>
            <div style={{ padding: '20px 24px', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#1e293b' }}>Danh Sách Tòa Nhà Cho Thuê</h2>
              <button 
                onClick={() => setEditingBuilding({})}
                style={{ padding: '8px 18px', background: '#e31c5f', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 700, cursor: 'pointer' }}
              >
                + Thêm văn phòng mới
              </button>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#475569', fontWeight: 700 }}>
                    <th style={{ padding: '16px' }}>Hình ảnh</th>
                    <th style={{ padding: '16px' }}>Tên tòa nhà</th>
                    <th style={{ padding: '16px' }}>Khu vực</th>
                    <th style={{ padding: '16px' }}>Phân hạng</th>
                    <th style={{ padding: '16px' }}>Giá thuê</th>
                    <th style={{ padding: '16px', textAlign: 'center' }}>Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  {buildings.map(b => (
                    <tr key={b.id} style={{ borderBottom: '1px solid #e2e8f0', verticalAlign: 'middle' }}>
                      <td style={{ padding: '16px' }}>
                        <img 
                          src={b.imageUrl || b.image || '/assets/modern_office_generic.jpg'} 
                          alt={b.name} 
                          style={{ width: '60px', height: '45px', objectFit: 'cover', borderRadius: '4px', border: '1px solid #eee' }} 
                        />
                      </td>
                      <td style={{ padding: '16px', fontWeight: 700, color: '#0f172a' }}>
                        <span style={{ display: 'block' }}>{b.name}</span>
                        <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 400 }}>ID: {b.id}</span>
                      </td>
                      <td style={{ padding: '16px', color: '#475569' }}>
                        {b.district}
                      </td>
                      <td style={{ padding: '16px', fontWeight: 600 }}>
                        Hạng {b.grade}
                      </td>
                      <td style={{ padding: '16px', color: '#e31c5f', fontWeight: 700 }}>
                        ${b.price}/m²
                      </td>
                      <td style={{ padding: '16px', textAlign: 'center' }}>
                        <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                          <button 
                            onClick={() => setEditingBuilding(b)}
                            style={{ padding: '4px 10px', background: '#eff6ff', border: '1px solid #dbeafe', borderRadius: '4px', color: '#2563eb', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}
                          >
                            Sửa
                          </button>
                          <button 
                            onClick={() => handleDeleteBuilding(b.id)}
                            style={{ padding: '4px 10px', background: '#fef2f2', border: '1px solid #fee2e2', borderRadius: '4px', color: '#b91c1c', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}
                          >
                            Xóa
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
