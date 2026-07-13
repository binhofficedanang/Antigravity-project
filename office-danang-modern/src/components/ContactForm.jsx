import React, { useState } from 'react';
import { supabase } from '../utils/api';

/**
 * ContactForm component
 * 
 * Two modes:
 * 1. If hubspotPortalId and hubspotFormId are provided, renders HubSpot embedded form
 * 2. Otherwise, renders a standalone form that submits to a configurable endpoint
 * 
 * For HubSpot setup:
 * - Go to HubSpot > Marketing > Forms > Create Form
 * - Get the Portal ID and Form ID from the embed code
 * - Pass them as props: <ContactForm hubspotPortalId="12345" hubspotFormId="xxx-xxx" />
 */

// HubSpot Form API endpoint
const HUBSPOT_API = 'https://api.hsforms.com/submissions/v3/integration/submit';

export default function ContactForm({ buildingName, hubspotPortalId, hubspotFormId, onSuccess }) {
  const [form, setForm] = useState({ name: '', phone: '', email: '', note: '' });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name || !form.phone) return;

    setSubmitting(true);
    setError(null);

    try {
      // 1. Ghi nhận lead vào Supabase database
      const { error: dbError } = await supabase
        .from('leads')
        .insert([{
          name: form.name,
          phone: form.phone,
          email: form.email || null,
          note: form.note || null,
          building_name: buildingName || 'Trang chủ',
          url: window.location.href
        }]);

      if (dbError) {
        console.error('Error inserting lead to Supabase:', dbError);
        // We will continue sending telegram even if db fails, or throw error depending on strictness.
        // Let's throw to handle error robustly.
        throw new Error(dbError.message);
      }

      // 2. TELEGRAM BOT CONFIGURATION (Optional - if set up later)
      const TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN';
      const TELEGRAM_CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID';

      if (TELEGRAM_BOT_TOKEN !== 'YOUR_TELEGRAM_BOT_TOKEN') {
        const message = `🔔 **CÓ KHÁCH LIÊN HỆ MỚI** 🔔\n\n`
          + `👤 Tên: ${form.name}\n`
          + `📞 SĐT: ${form.phone}\n`
          + `✉️ Email: ${form.email || 'Không có'}\n`
          + `🏢 Tòa nhà: ${buildingName || 'Trang chủ'}\n`
          + `📝 Ghi chú: ${form.note || 'Không có'}\n`
          + `🔗 Nguồn: ${window.location.href}`;

        const telegramApi = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
        await fetch(telegramApi, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            chat_id: TELEGRAM_CHAT_ID,
            text: message,
            parse_mode: 'Markdown',
          }),
        }).catch(err => console.error('Telegram notification error:', err));
      }

      // Success
      setSubmitted(true);
      setForm({ name: '', phone: '', email: '', note: '' });
      if (onSuccess) onSuccess();
      
      setTimeout(() => setSubmitted(false), 5000);
    } catch (err) {
      console.error('Form submission error:', err);
      setError('Gửi không thành công. Vui lòng thử lại hoặc gọi hotline 0987 667 270.');
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="contact-form-card">
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: 12 }}>✅</div>
          <h3 style={{ border: 'none', padding: 0, marginBottom: 8 }}>Gửi yêu cầu thành công!</h3>
          <p>Chúng tôi sẽ liên hệ bạn trong vòng 30 phút.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="contact-form-card" id="contact" style={{ background: '#fff', border: '1px solid #eee', padding: '24px', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
      {!showForm ? (
        <div className="contact-sidebar-cta">
          <h3 style={{ textAlign: 'center', fontSize: '1.4rem', color: '#333', marginBottom: '16px', fontWeight: 'bold' }}>Liên hệ</h3>
          
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '24px' }}>
            <div style={{ width: '20px', height: '20px', background: '#00a550', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '12px' }}>✓</div>
            <span style={{ fontSize: '0.95rem', fontWeight: 600, color: '#333' }}>Tư vấn hoàn toàn miễn phí.</span>
          </div>

          <a href="tel:0987667270" style={{ display: 'block', width: '100%', background: '#e31c5f', color: '#fff', textAlign: 'center', padding: '14px', borderRadius: '6px', fontWeight: 'bold', fontSize: '1.1rem', marginBottom: '12px', textDecoration: 'none' }}>
            Gọi 0987.667.270
          </a>
          
          <button onClick={() => setShowForm(true)} style={{ display: 'block', width: '100%', background: '#fff', border: '1px solid #e31c5f', color: '#e31c5f', textAlign: 'center', padding: '14px', borderRadius: '6px', fontWeight: 'bold', fontSize: '1rem', cursor: 'pointer', marginBottom: '32px' }}>
            Nhận báo giá & Đặt lịch đi xem
          </button>
          
          <p style={{ textAlign: 'center', fontSize: '0.95rem', color: '#333', marginBottom: '16px' }}>Chuyên viên tư vấn sẵn sàng hỗ trợ 24/7</p>
        </div>
      ) : (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#333', fontWeight: 'bold' }}>Nhận báo giá chi tiết</h3>
            <button onClick={() => setShowForm(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.2rem', color: '#999' }}>✕</button>
          </div>
          <p style={{ fontSize: '0.85rem', color: '#666', marginBottom: '20px' }}>Điền thông tin để nhận bảng báo giá &amp; diện tích trống mới nhất.</p>
          {error && <div style={{ background: '#fff0f0', border: '1px solid #ffcdd2', borderRadius: 6, padding: '8px 12px', marginBottom: 12, color: '#c62828', fontSize: '0.85rem' }}>{error}</div>}
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-field">
                <label className="form-label">Họ tên *</label>
                <input className="form-input" placeholder="Nguyễn Văn A" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div className="form-field">
                <label className="form-label">Số điện thoại *</label>
                <input className="form-input" type="tel" placeholder="09xx xxx xxx" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} required />
              </div>
            </div>
            <div className="form-field">
              <label className="form-label">Email</label>
              <input className="form-input" type="email" placeholder="name@company.com" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
            </div>
            <div className="form-field">
              <label className="form-label">Yêu cầu / Lưu ý</label>
              <textarea className="form-input" rows="3" placeholder="Cần thuê 150m², chuyển vào Quý tới..." value={form.note} onChange={e => setForm({ ...form, note: e.target.value })} />
            </div>
            <button type="submit" className="btn-submit" disabled={submitting}>
              {submitting ? 'Đang gửi...' : 'Gửi yêu cầu báo giá'}
            </button>
          </form>
        </>
      )}
    </div>
  );
}
