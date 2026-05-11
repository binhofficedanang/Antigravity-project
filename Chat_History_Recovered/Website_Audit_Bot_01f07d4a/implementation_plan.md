# Website Audit Bot - Kế hoạch triển khai

Xây dựng một bot Python tự động **quét và kiểm tra toàn diện website**, tạo báo cáo HTML/PDF chi tiết về tình trạng SEO, hiệu suất, bảo mật và trải nghiệm người dùng.

---

## Tính năng kiểm tra

### 🔍 SEO Audit
- **On-page SEO**: Title tag, meta description, H1-H6 hierarchy
- **URL structure**: Canonical, slug, breadcrumb
- **Image audit**: Alt text thiếu, kích thước ảnh quá lớn
- **Internal/External links**: Broken links, redirect chains
- **Schema Markup**: Detect structured data (JSON-LD)
- **Keyword density**: Phân tích từ khóa trong nội dung

### ⚡ Performance Audit
- **Core Web Vitals**: LCP, FID, CLS (via Google PageSpeed API)
- **Page load time**: TTFB, First Paint
- **Resource size**: JS/CSS/Image bloat
- **Caching headers**: Cache-Control, ETag

### 🔒 Security Audit
- **HTTPS check**: SSL certificate validity, expiry date
- **Security headers**: X-Frame-Options, CSP, HSTS, X-XSS-Protection
- **Robots.txt & Sitemap.xml**: Tồn tại và hợp lệ
- **Mixed content**: HTTP resources trên HTTPS page

### 📱 Technical Audit
- **Mobile-friendly**: Viewport meta tag, responsive check
- **404 pages**: Crawl và phát hiện broken pages
- **Redirect chains**: 301/302 redirect loops
- **Duplicate content**: Canonical issues
- **Crawl depth**: Số lượng click từ homepage

---

## Đầu ra (Output)

- 📊 **HTML Report** đẹp với biểu đồ, màu sắc (xanh/vàng/đỏ) theo mức độ nghiêm trọng
- 📄 **JSON data file** để tái sử dụng hoặc tích hợp với hệ thống khác
- 📋 **Console summary** với điểm audit tổng hợp (0-100)

---

## Kiến trúc hệ thống

```
Website Audit Bot/
├── main_audit.py           # Entry point - chạy toàn bộ audit
├── config.json             # Cấu hình URL, API keys, depth
├── modules/
│   ├── seo_auditor.py      # Kiểm tra SEO on-page
│   ├── performance.py      # PageSpeed API + load time
│   ├── security.py         # HTTPS, headers, robots
│   ├── crawler.py          # Spider crawl toàn bộ site
│   └── link_checker.py     # Broken links, redirects
├── report/
│   ├── report_generator.py # Tạo HTML report
│   └── template.html       # Template báo cáo đẹp
└── reports/                # Thư mục lưu báo cáo output
```

---

## Thư viện Python sử dụng

| Thư viện | Mục đích |
|----------|----------|
| `requests` + `httpx` | HTTP requests, check status codes |
| `BeautifulSoup4` | Parse HTML, extract tags |
| `scrapy` hoặc custom crawler | Crawl toàn bộ website |
| `ssl` + `socket` | Kiểm tra SSL certificate |
| `Google PageSpeed API` | Core Web Vitals, performance score |
| `jinja2` | Render HTML report template |
| `rich` | Console output đẹp |
| `concurrent.futures` | Chạy song song nhiều URL |

---

## Open Questions

> [!IMPORTANT]
> **Câu hỏi 1**: Bạn muốn audit **một trang cụ thể** hay **crawl toàn bộ website** (theo độ sâu)?

> [!IMPORTANT]  
> **Câu hỏi 2**: Bạn có **Google PageSpeed Insights API key** không? Nếu không có thì chỉ dùng thư viện local để đo.

> [!NOTE]
> **Câu hỏi 3**: Output muốn là **HTML report mở trên browser**, hay **PDF**, hay chỉ cần **console + JSON** thôi?

> [!NOTE]
> **Câu hỏi 4**: Website của bạn là **WordPress** hay nền tảng khác? (Có một số check đặc biệt cho WP như Yoast/Rank Math score)

---

## Verification Plan

### Automated Tests
- Chạy audit trên `https://example.com` để test
- Kiểm tra output file được tạo đúng format
- Verify tất cả modules không throw exception

### Manual Verification
- Mở HTML report trên browser kiểm tra giao diện
- So sánh kết quả với GTmetrix / Screaming Frog để validate độ chính xác
