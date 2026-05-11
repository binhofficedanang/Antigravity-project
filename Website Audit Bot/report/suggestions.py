"""
Fix Suggestions Dictionary
Mỗi key tương ứng với một vấn đề → cung cấp hướng dẫn sửa lỗi chi tiết cho WordPress
"""

SUGGESTIONS = {

    # ══════════════════════════════════════════════════════════════
    # SEO
    # ══════════════════════════════════════════════════════════════
    "missing_title": {
        "title": "Thiếu Title Tag",
        "severity": "critical",
        "why": "Title tag là yếu tố SEO quan trọng nhất, Google dùng nó để hiển thị kết quả tìm kiếm.",
        "steps": [
            "Cài Rank Math SEO (miễn phí) hoặc Yoast SEO plugin nếu chưa có",
            "Mở bài viết/trang trong WordPress Editor",
            "Tìm ô 'SEO Title' trong panel Rank Math bên phải",
            "Nhập title chứa từ khóa chính, độ dài 50–60 ký tự",
            "Lưu bài và kiểm tra lại"
        ],
        "wp_tip": "Rank Math → Post Settings → SEO Title: dùng biến %title% – %sep% – %sitename%"
    },
    "short_title": {
        "title": "Title Tag Quá Ngắn",
        "severity": "warning",
        "why": "Title ngắn hơn 50 ký tự lãng phí không gian hiển thị trên Google SERP.",
        "steps": [
            "Mở Rank Math SEO panel trên bài viết",
            "Mở rộng title bằng cách thêm từ khóa phụ hoặc tên thương hiệu",
            "Mục tiêu: 50–60 ký tự"
        ],
        "wp_tip": "Dùng công thức: [Từ khóa chính] – [Từ khóa phụ] | [Tên thương hiệu]"
    },
    "long_title": {
        "title": "Title Tag Quá Dài",
        "severity": "warning",
        "why": "Google cắt title > 60 ký tự, hiển thị dấu '...' và mất thông tin quan trọng.",
        "steps": [
            "Rút ngắn title xuống dưới 60 ký tự",
            "Ưu tiên giữ từ khóa chính ở đầu câu",
            "Bỏ các từ không cần thiết như 'và', 'của', 'để'"
        ],
        "wp_tip": "Rank Math có thanh đếm ký tự màu xanh/đỏ để hướng dẫn độ dài chuẩn"
    },
    "missing_meta_desc": {
        "title": "Thiếu Meta Description",
        "severity": "critical",
        "why": "Meta description ảnh hưởng đến click-through rate (CTR) trên Google. Thiếu nó Google sẽ tự chọn đoạn text ngẫu nhiên.",
        "steps": [
            "Mở Rank Math SEO panel trên bài viết",
            "Điền 'Meta Description' khoảng 150–160 ký tự",
            "Phải chứa từ khóa chính và lời kêu gọi hành động (CTA)"
        ],
        "wp_tip": "Rank Math → Meta Description → Nên có từ khóa và CTA như 'Đọc ngay', 'Tìm hiểu thêm'"
    },
    "short_meta_desc": {
        "title": "Meta Description Quá Ngắn",
        "severity": "warning",
        "why": "Meta description ngắn không tận dụng được không gian hiển thị trên SERP.",
        "steps": ["Mở rộng meta description lên 150–160 ký tự", "Thêm lợi ích, từ khóa phụ hoặc CTA"],
        "wp_tip": None
    },
    "long_meta_desc": {
        "title": "Meta Description Quá Dài",
        "severity": "warning",
        "why": "Google sẽ cắt bớt meta description > 160 ký tự.",
        "steps": ["Rút ngắn xuống 150–160 ký tự", "Đặt thông tin quan trọng nhất ở đầu"],
        "wp_tip": None
    },
    "missing_h1": {
        "title": "Thiếu Thẻ H1",
        "severity": "critical",
        "why": "H1 là tiêu đề chính của trang, Google coi đây là yếu tố xác định chủ đề nội dung.",
        "steps": [
            "Kiểm tra theme WordPress của bạn có tự thêm H1 không",
            "Trong WordPress Editor, tiêu đề bài viết thường là H1",
            "Nếu dùng Page Builder (Elementor), thêm widget Heading và chọn H1",
            "Đảm bảo chứa từ khóa chính"
        ],
        "wp_tip": "WordPress mặc định: tiêu đề bài viết (<h1 class='entry-title'>) = H1 tag"
    },
    "multiple_h1": {
        "title": "Nhiều Thẻ H1",
        "severity": "warning",
        "why": "Nhiều H1 gây nhầm lẫn cho Google về chủ đề chính của trang.",
        "steps": [
            "Dùng browser DevTools (F12) để tìm tất cả H1 tags",
            "Đổi các H1 thừa thành H2 hoặc H3",
            "Chỉ giữ lại 1 H1 duy nhất chứa từ khóa chính"
        ],
        "wp_tip": "Elementor: kiểm tra từng widget Heading và đổi tag sang H2"
    },
    "missing_alt": {
        "title": "Ảnh Thiếu Alt Text",
        "severity": "warning",
        "why": "Alt text giúp Google hiểu nội dung ảnh và cải thiện SEO hình ảnh.",
        "steps": [
            "Vào WordPress Media Library",
            "Click vào từng ảnh và điền 'Alternative Text'",
            "Hoặc trong bài viết, click ảnh → 'Alt text' bên panel phải",
            "Mô tả ngắn gọn nội dung ảnh, có thể chứa từ khóa tự nhiên"
        ],
        "wp_tip": "Plugin 'Automatic Alt Text' hoặc Rank Math có tính năng tự động gợi ý alt text"
    },
    "missing_canonical": {
        "title": "Thiếu Canonical Tag",
        "severity": "warning",
        "why": "Canonical tag ngăn duplicate content khi URL có nhiều dạng khác nhau.",
        "steps": [
            "Cài Rank Math hoặc Yoast SEO – cả hai tự động thêm canonical",
            "Kiểm tra Settings → General → Canonical URL trong Rank Math"
        ],
        "wp_tip": "Rank Math tự động thêm canonical tag cho mọi bài viết/trang"
    },
    "missing_og": {
        "title": "Thiếu Open Graph Tags",
        "severity": "warning",
        "why": "Open Graph tags kiểm soát cách nội dung hiển thị khi share lên Facebook, LinkedIn...",
        "steps": [
            "Cài Rank Math SEO",
            "Vào Rank Math → Settings → General → Social Meta",
            "Bật 'Open Graph Meta Tags'",
            "Mỗi bài viết: thêm ảnh thumbnail đúng kích thước 1200x630px"
        ],
        "wp_tip": "Rank Math → Post → Social → Custom OG Image để kiểm soát ảnh share"
    },
    "missing_schema": {
        "title": "Thiếu Schema Markup",
        "severity": "warning",
        "why": "Schema giúp Google hiểu nội dung sâu hơn và hiển thị rich snippets (sao, giá, FAQ...).",
        "steps": [
            "Rank Math tự động thêm Schema cho Article, BlogPost",
            "Vào Rank Math → Post → Schema tab → chọn loại schema phù hợp",
            "Cho trang FAQ: thêm FAQ schema để có rich snippet",
            "Kiểm tra tại: search.google.com/test/rich-results"
        ],
        "wp_tip": "Rank Math PRO hỗ trợ schema nâng cao: Review, Recipe, HowTo..."
    },
    "missing_viewport": {
        "title": "Thiếu Viewport Meta Tag",
        "severity": "critical",
        "why": "Không có viewport tag khiến trang hiển thị sai trên mobile, Google penalize.",
        "steps": [
            "Vào WordPress → Appearance → Theme Editor → header.php",
            "Thêm vào trong <head>: <meta name='viewport' content='width=device-width, initial-scale=1'>",
            "Hoặc dùng theme hiện đại đã có sẵn viewport tag"
        ],
        "wp_tip": "Hầu hết WordPress theme từ 2015 đã có viewport tag. Nếu không, nên đổi theme"
    },
    "thin_content": {
        "title": "Nội Dung Mỏng (Thin Content)",
        "severity": "warning",
        "why": "Trang < 300 từ khó xếp hạng và có thể bị Google đánh giá là low-quality.",
        "steps": [
            "Mở rộng nội dung lên ít nhất 600–1000 từ",
            "Thêm phần FAQ, thông tin chi tiết, ví dụ thực tế",
            "Dùng SEO bot để tạo nội dung dài hơn với chủ đề tương tự"
        ],
        "wp_tip": "Rank Math → Content Analysis → kiểm tra 'Content Length' score"
    },
    "missing_h2": {
        "title": "Thiếu Thẻ H2",
        "severity": "warning",
        "why": "H2 tags giúp cấu trúc nội dung, cải thiện readability và SEO.",
        "steps": [
            "Chia nội dung bài viết thành các phần với tiêu đề H2",
            "Mỗi H2 nên chứa từ khóa phụ hoặc LSI keywords",
            "Nên có 3–5 H2 cho bài viết dài"
        ],
        "wp_tip": None
    },
    "low_internal_links": {
        "title": "Ít Internal Links",
        "severity": "warning",
        "why": "Internal linking giúp Google crawl site và phân phối PageRank.",
        "steps": [
            "Thêm ít nhất 3–5 internal links trong mỗi bài viết",
            "Link đến các bài viết liên quan cùng chủ đề",
            "Dùng anchor text có ý nghĩa, chứa từ khóa"
        ],
        "wp_tip": "Plugin 'Link Whisper' tự động gợi ý internal links phù hợp"
    },
    "missing_seo_plugin": {
        "title": "Không Có SEO Plugin",
        "severity": "warning",
        "why": "SEO plugin giúp tối ưu meta tags, schema, sitemap tự động.",
        "steps": [
            "Vào WordPress → Plugins → Add New",
            "Tìm 'Rank Math SEO' → Install → Activate",
            "Chạy Setup Wizard để cấu hình cơ bản",
            "Kết nối với Google Search Console"
        ],
        "wp_tip": "Rank Math free version đủ mạnh cho hầu hết websites"
    },
    "wp_version_exposed": {
        "title": "WordPress Version Bị Lộ",
        "severity": "warning",
        "why": "Lộ version WordPress giúp hacker biết lỗ hổng để tấn công.",
        "steps": [
            "Thêm vào functions.php: remove_action('wp_head', 'wp_generator');",
            "Cài plugin 'Hide My WP Ghost' để ẩn toàn bộ thông tin WP",
            "Cập nhật WordPress lên phiên bản mới nhất thường xuyên"
        ],
        "wp_tip": "functions.php: add_filter('the_generator', '__return_empty_string');"
    },

    # ══════════════════════════════════════════════════════════════
    # SECURITY
    # ══════════════════════════════════════════════════════════════
    "no_https": {
        "title": "Trang Không Dùng HTTPS",
        "severity": "critical",
        "why": "HTTPS là yếu tố xếp hạng của Google. HTTP gây cảnh báo 'Không an toàn' trên Chrome.",
        "steps": [
            "Đăng ký SSL certificate miễn phí qua Let's Encrypt",
            "Hosting cPanel: Security → Let's Encrypt SSL → Issue",
            "Sau khi bật SSL, vào WordPress Settings → General → đổi URL sang https://",
            "Cài plugin 'Really Simple SSL' để tự động redirect HTTP → HTTPS"
        ],
        "wp_tip": "Plugin 'Really Simple SSL' xử lý mọi redirect và mixed content tự động"
    },
    "ssl_expired": {
        "title": "SSL Certificate Đã Hết Hạn",
        "severity": "critical",
        "why": "SSL hết hạn khiến trình duyệt hiển thị cảnh báo, người dùng sẽ rời đi ngay.",
        "steps": [
            "Đăng nhập hosting control panel",
            "Vào SSL/TLS Manager → Renew certificate",
            "Let's Encrypt tự gia hạn mỗi 90 ngày nếu cấu hình đúng"
        ],
        "wp_tip": None
    },
    "ssl_expiring": {
        "title": "SSL Sắp Hết Hạn",
        "severity": "warning",
        "why": "SSL hết hạn gây gián đoạn website nghiêm trọng.",
        "steps": [
            "Gia hạn SSL ngay trong hosting control panel",
            "Bật Auto-Renewal cho Let's Encrypt"
        ],
        "wp_tip": None
    },
    "ssl_invalid": {
        "title": "SSL Certificate Không Hợp Lệ",
        "severity": "critical",
        "why": "SSL không hợp lệ khiến Chrome hiển thị trang cảnh báo đỏ.",
        "steps": [
            "Xóa SSL hiện tại và cài lại Let's Encrypt",
            "Đảm bảo domain trong certificate khớp với domain website"
        ],
        "wp_tip": None
    },
    "missing_xframe": {
        "title": "Thiếu X-Frame-Options Header",
        "severity": "warning",
        "why": "Không có header này cho phép kẻ tấn công nhúng site vào iframe (clickjacking attack).",
        "steps": [
            "Thêm vào .htaccess: Header always append X-Frame-Options SAMEORIGIN",
            "Hoặc cài plugin 'HTTP Headers' để quản lý security headers dễ dàng"
        ],
        "wp_tip": "Plugin 'Headers Security Advanced & HSTS WP' tự động thêm tất cả headers"
    },
    "missing_hsts": {
        "title": "Thiếu HSTS Header",
        "severity": "warning",
        "why": "HSTS buộc trình duyệt luôn dùng HTTPS, ngăn SSL stripping attack.",
        "steps": [
            "Thêm vào .htaccess: Header always set Strict-Transport-Security 'max-age=31536000'",
            "Sau khi HTTPS ổn định 100%, thêm includeSubDomains"
        ],
        "wp_tip": None
    },
    "missing_xcto": {
        "title": "Thiếu X-Content-Type-Options",
        "severity": "warning",
        "why": "Ngăn trình duyệt đoán sai content type (MIME sniffing attacks).",
        "steps": ["Thêm .htaccess: Header always set X-Content-Type-Options nosniff"],
        "wp_tip": None
    },
    "missing_referrer": {
        "title": "Thiếu Referrer-Policy",
        "severity": "warning",
        "why": "Kiểm soát thông tin referrer được gửi khi user click link ra ngoài.",
        "steps": ["Thêm .htaccess: Header always set Referrer-Policy 'strict-origin-when-cross-origin'"],
        "wp_tip": None
    },
    "missing_csp": {
        "title": "Thiếu Content-Security-Policy",
        "severity": "warning",
        "why": "CSP ngăn XSS attacks bằng cách giới hạn sources của scripts, styles...",
        "steps": [
            "CSP phức tạp, cần test kỹ trước khi deploy",
            "Bắt đầu với Content-Security-Policy-Report-Only để monitor",
            "Dùng tool: csp-evaluator.withgoogle.com"
        ],
        "wp_tip": "Plugin 'HTTP Headers' có wizard tạo CSP header"
    },
    "mixed_content": {
        "title": "Mixed Content Phát Hiện",
        "severity": "warning",
        "why": "HTTP resources trên HTTPS page làm trang kém an toàn và có thể bị block.",
        "steps": [
            "Cài plugin 'Really Simple SSL' → bật 'Mixed content fixer'",
            "Hoặc dùng plugin 'Better Search Replace' để thay http:// → https:// trong database",
            "Kiểm tra với: why-no-padlock.com"
        ],
        "wp_tip": "Really Simple SSL → Settings → Mixed content fixer → Enable"
    },
    "missing_robots": {
        "title": "Thiếu robots.txt",
        "severity": "warning",
        "why": "robots.txt hướng dẫn Google bot những trang nào nên/không nên crawl.",
        "steps": [
            "Rank Math → General Settings → Generate robots.txt tự động",
            "Hoặc tạo file /robots.txt thủ công với nội dung cơ bản:",
            "User-agent: *\\nAllow: /\\nSitemap: https://yoursite.com/sitemap.xml"
        ],
        "wp_tip": "Yoast/Rank Math đều có công cụ tạo và chỉnh robots.txt trong dashboard"
    },
    "missing_sitemap": {
        "title": "Thiếu Sitemap XML",
        "severity": "warning",
        "why": "Sitemap giúp Google khám phá và index tất cả trang nhanh hơn.",
        "steps": [
            "Rank Math → Sitemap Settings → Enable Sitemap",
            "Sau đó submit sitemap vào Google Search Console",
            "URL sitemap thường là: yoursite.com/sitemap_index.xml"
        ],
        "wp_tip": "Rank Math → Sitemap → Submit URL vào Google Search Console → Sitemaps"
    },

    # ══════════════════════════════════════════════════════════════
    # PERFORMANCE
    # ══════════════════════════════════════════════════════════════
    "slow_page": {
        "title": "Trang Tải Chậm",
        "severity": "critical",
        "why": "Google dùng tốc độ tải là yếu tố xếp hạng. Trang chậm tăng bounce rate.",
        "steps": [
            "Cài WP Rocket hoặc LiteSpeed Cache (plugin tốt nhất)",
            "Bật Page Caching, Browser Caching, GZIP Compression",
            "Dùng CDN như Cloudflare (miễn phí)",
            "Tối ưu ảnh bằng plugin ShortPixel hoặc Smush",
            "Giảm số plugin không cần thiết"
        ],
        "wp_tip": "WP Rocket = plugin cache tốt nhất, LiteSpeed Cache miễn phí tốt không kém"
    },
    "large_page_size": {
        "title": "Kích Thước Trang Quá Lớn",
        "severity": "warning",
        "why": "Trang nặng tải chậm, đặc biệt trên mobile và 4G.",
        "steps": [
            "Nén ảnh bằng ShortPixel hoặc Imagify",
            "Minify CSS/JS bằng WP Rocket hoặc Autoptimize",
            "Lazy load ảnh và video",
            "Xóa CSS/JS không dùng đến"
        ],
        "wp_tip": "WP Rocket → File Optimization → Minify CSS & JS, Combine CSS & JS"
    },
    "low_pagespeed": {
        "title": "PageSpeed Score Thấp",
        "severity": "critical",
        "why": "Core Web Vitals là yếu tố xếp hạng chính thức của Google từ 2021.",
        "steps": [
            "Xem chi tiết tại: pagespeed.web.dev",
            "Ưu tiên fix: LCP, CLS, FID",
            "Cài WP Rocket + Cloudflare CDN",
            "Preload LCP image",
            "Defer non-critical JavaScript"
        ],
        "wp_tip": "WP Rocket → Media → LazyLoad, Optimize Images for Google PageSpeed"
    },
    "bad_lcp": {
        "title": "LCP (Largest Contentful Paint) Chậm",
        "severity": "critical",
        "why": "LCP > 2.5s bị Google đánh giá 'Cần cải thiện', ảnh hưởng xếp hạng.",
        "steps": [
            "Preload LCP image: thêm <link rel='preload'> cho ảnh hero",
            "Dùng CDN để giảm latency",
            "Tối ưu server response time (TTFB < 200ms)",
            "Lazy load ảnh bên dưới fold, không lazy load ảnh hero"
        ],
        "wp_tip": "WP Rocket → Preload → Enable Link Preloading"
    },
    "bad_cls": {
        "title": "CLS (Layout Shift) Cao",
        "severity": "warning",
        "why": "CLS > 0.1 khiến trang 'nhảy layout' khi load, trải nghiệm xấu.",
        "steps": [
            "Đặt width/height cho tất cả ảnh và video",
            "Tránh chèn nội dung dynamic phía trên fold",
            "Reserve space cho ads và embeds"
        ],
        "wp_tip": "Thêm aspect-ratio CSS cho container ảnh để tránh layout shift"
    },

    # ══════════════════════════════════════════════════════════════
    # TECHNICAL
    # ══════════════════════════════════════════════════════════════
    "broken_links": {
        "title": "Broken Links (404)",
        "severity": "critical",
        "why": "Broken links làm xấu UX và lãng phí crawl budget của Google.",
        "steps": [
            "Cài plugin 'Broken Link Checker' để tự động phát hiện",
            "Fix broken links bằng cách cập nhật URL hoặc xóa link",
            "Cài plugin 'Redirection' để tạo 301 redirect nếu URL đã thay đổi"
        ],
        "wp_tip": "Plugin 'Redirection' cho phép quản lý 301 redirects trực tiếp trong WordPress"
    },
    "redirect_chains": {
        "title": "Redirect Chain Dài",
        "severity": "warning",
        "why": "Redirect chain > 2 hops làm chậm tải trang và giảm PageRank transfer.",
        "steps": [
            "Dùng plugin Redirection để xem danh sách redirects",
            "Sửa để redirect thẳng từ A → C, bỏ qua B",
            "Kiểm tra chuỗi redirect: httpstatus.io"
        ],
        "wp_tip": "Redirection plugin → Redirects → kiểm tra source và target URLs"
    },

    # Fallback
    "fetch_error": {
        "title": "Không Thể Tải Trang",
        "severity": "critical",
        "why": "Bot không thể kết nối đến URL này.",
        "steps": [
            "Kiểm tra URL có đúng không",
            "Đảm bảo website đang online",
            "Kiểm tra firewall không block bot user-agent"
        ],
        "wp_tip": None
    },
}


def get_suggestion(key):
    """Trả về suggestion dict cho một issue key, hoặc None nếu không tìm thấy"""
    return SUGGESTIONS.get(key)
