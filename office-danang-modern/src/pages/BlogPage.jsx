import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useSEO } from '../utils/seo';
import { postsData as posts } from '../data/posts';

export default function BlogPage() {
  const { slug } = useParams();
  const [toc, setToc] = useState([]);
  
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [slug]);

  const post = slug ? posts.find(p => p.slug === slug) : null;

  useEffect(() => {
    if (!post) return;
    const contentDiv = document.querySelector('.blog-content');
    if (contentDiv) {
      const headings = contentDiv.querySelectorAll('h2, h3');
      const tocList = [];
      headings.forEach((heading, index) => {
        const id = `heading-${index}`;
        heading.id = id;
        tocList.push({ id, text: heading.textContent, level: heading.tagName.toLowerCase() });
      });
      setToc(tocList);
    }
  }, [post]);

  useSEO({
    title: slug 
      ? (post ? `${post.title} | Kinh nghiệm thuê` : '') 
      : 'Kinh nghiệm thuê văn phòng Đà Nẵng | Office43',
    description: slug 
      ? (post ? post.excerpt : '') 
      : 'Tổng hợp kinh nghiệm thuê văn phòng tại Đà Nẵng, các mẹo đàm phán, review tòa nhà giúp doanh nghiệp tối ưu chi phí.',
    schema: post ? {
      "@context": "https://schema.org",
      "@type": "BlogPosting",
      "headline": post.title,
      "datePublished": post.date,
      "description": post.excerpt,
      "publisher": { "@type": "Organization", "name": "Office43" }
    } : null
  });


  // LIST VIEW
  if (!slug) {
    return (
      <main>
        <div className="container" style={{ padding: '60px 0' }}>
          <div className="section-header" style={{ marginBottom: 40 }}>
            <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>Kinh nghiệm thuê văn phòng</h1>
            <p className="desc" style={{ maxWidth: 800, margin: '12px auto 0' }}>
              Kiến thức thực tiễn và lời khuyên chuyên gia để quá trình tìm kiếm không gian làm việc của bạn trở nên dễ dàng hơn.
            </p>
          </div>

          <div className="blog-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))' }}>
            {posts.map((p, i) => (
              <Link to={`/blog/${p.slug}`} className="blog-card" key={i}>
                <div className="blog-card-img"><img src={p.image} alt={p.title} loading="lazy" /></div>
                <div className="blog-card-body">
                  <h4>{p.title}</h4>
                  <p className="excerpt">{p.excerpt}</p>
                  <div style={{ fontSize: '0.8rem', color: '#999', marginTop: 12 }}>{p.date}</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </main>
    );
  }

  // DETAIL VIEW
  if (!post) return <div style={{ textAlign: 'center', padding: '100px', minHeight: '60vh' }}><h3>Bài viết không tồn tại</h3><Link to="/blog">Về danh sách bài viết</Link></div>;

  return (
    <main>
      <div className="container" style={{ maxWidth: 800, padding: '40px 0 80px' }}>
        <div className="breadcrumb-bar" style={{ marginBottom: 32, padding: 0, border: 'none' }}>
          <div className="breadcrumb-list">
            <Link to="/">Trang chủ</Link>
            <span className="breadcrumb-sep">›</span>
            <Link to="/blog">Kinh nghiệm thuê</Link>
            <span className="breadcrumb-sep">›</span>
            <span>{post.title}</span>
          </div>
        </div>
        <article className="blog-detail">
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800, lineHeight: 1.3, marginBottom: 16 }}>{post.title}</h1>
          <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: 32 }}>Xuất bản: {post.date}</div>
          
          <img 
            src={post.image} 
            alt={post.title} 
            style={{ width: '100%', borderRadius: 12, marginBottom: 40, maxHeight: 400, objectFit: 'cover' }} 
          />
          
          {toc.length > 0 && (
            <div className="blog-toc" style={{ backgroundColor: '#f8f9fa', padding: '24px', borderRadius: 12, marginBottom: 40, borderLeft: '4px solid #0056b3' }}>
              <h3 style={{ fontSize: '1.2rem', marginBottom: 16, marginTop: 0 }}>Nội dung chính</h3>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {toc.map((item, i) => (
                  <li key={i} style={{ marginBottom: 12, paddingLeft: item.level === 'h3' ? 20 : 0 }}>
                    <a 
                      href={`#${item.id}`} 
                      onClick={(e) => {
                        e.preventDefault();
                        const element = document.getElementById(item.id);
                        if (element) {
                          const y = element.getBoundingClientRect().top + window.pageYOffset - 80;
                          window.scrollTo({ top: y, behavior: 'smooth' });
                        }
                      }}
                      style={{ color: '#333', textDecoration: 'none', fontWeight: item.level === 'h2' ? 600 : 400 }}
                    >
                      {item.text}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          <div className="blog-content" style={{ fontSize: '1.05rem', lineHeight: 1.8, color: '#333' }}>
            <div dangerouslySetInnerHTML={{ __html: post.content.replace(/\n/g, '<br/>') }} />
          </div>

          <div className="blog-cta-block" style={{ backgroundColor: '#eef6ff', padding: '40px 24px', borderRadius: 16, marginTop: 60, textAlign: 'center', border: '1px solid #cce3ff' }}>
            <h3 style={{ fontSize: '1.5rem', color: '#0056b3', marginBottom: 16, marginTop: 0 }}>Bạn đang tìm không gian làm việc lý tưởng?</h3>
            <p style={{ color: '#555', marginBottom: 32, fontSize: '1.05rem' }}>Office43 hỗ trợ tư vấn, tìm kiếm và đàm phán hợp đồng văn phòng <strong>hoàn toàn miễn phí</strong>. Nhận báo giá mặt bằng trống mới nhất ngay hôm nay!</p>
            <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
              <a href="tel:0935723727" className="btn btn-primary" style={{ padding: '12px 24px', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                Gọi: 0935.723.727
              </a>
              <Link to="/" className="btn" style={{ padding: '12px 24px', fontWeight: 600, backgroundColor: '#fff', color: '#0056b3', border: '2px solid #0056b3' }}>
                Xem danh sách tòa nhà
              </Link>
            </div>
          </div>
        </article>

        <div style={{ marginTop: 60, paddingTop: 40, borderTop: '1px solid #eee' }}>
          <h3 style={{ marginBottom: 20 }}>Bài viết mới nhất</h3>
          <div className="blog-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
            {posts.filter(p => p.slug !== slug).slice(0, 2).map((p, i) => (
              <Link to={`/blog/${p.slug}`} className="blog-card" key={i}>
                <div className="blog-card-img"><img src={p.image} alt={p.title} loading="lazy" /></div>
                <div className="blog-card-body">
                  <h4>{p.title}</h4>
                  <p className="excerpt">{p.excerpt}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
