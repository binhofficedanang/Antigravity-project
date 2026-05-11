"""
SEO Auditor Module
Kiểm tra toàn diện các yếu tố SEO on-page của một trang web
"""
import re
import requests
from bs4 import BeautifulSoup


class SEOAuditor:
    def __init__(self, config):
        self.config = config
        self.timeout = config.get('request_timeout', 15)
        self.user_agent = config.get('user_agent', 'WebsiteAuditBot/1.0')
        self.wp_enabled = config.get('wordpress', {}).get('enabled', False)

    def audit_page(self, url, html=None, soup=None):
        """Audit toàn bộ SEO issues cho một URL"""
        issues = []

        if soup is None:
            try:
                headers = {'User-Agent': self.user_agent}
                response = requests.get(url, headers=headers, timeout=self.timeout)
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
            except Exception as e:
                return [self._issue('fetch_error', 'critical',
                                    f'Không thể tải trang: {e}', '', 'fetch_error')]

        # ─── TITLE TAG ───────────────────────────────────────────────────────────
        title_tag = soup.find('title')
        if not title_tag or not title_tag.text.strip():
            issues.append(self._issue('title_missing', 'critical',
                                      'Trang thiếu thẻ <title>', '', 'missing_title'))
        else:
            t = title_tag.text.strip()
            tlen = len(t)
            if tlen < 30:
                issues.append(self._issue('title_short', 'warning',
                                          f'Title quá ngắn ({tlen} ký tự, nên 50–60)', t, 'short_title'))
            elif tlen > 60:
                issues.append(self._issue('title_long', 'warning',
                                          f'Title quá dài ({tlen} ký tự, nên 50–60)', t, 'long_title'))
            else:
                issues.append(self._issue('title_ok', 'pass',
                                          f'Title hợp lệ ({tlen} ký tự)', t, None))

        # ─── META DESCRIPTION ────────────────────────────────────────────────────
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc or not meta_desc.get('content', '').strip():
            issues.append(self._issue('meta_desc_missing', 'critical',
                                      'Thiếu thẻ meta description', '', 'missing_meta_desc'))
        else:
            d = meta_desc['content'].strip()
            dlen = len(d)
            if dlen < 120:
                issues.append(self._issue('meta_desc_short', 'warning',
                                          f'Meta description ngắn ({dlen} ký tự, nên 150–160)', d[:120], 'short_meta_desc'))
            elif dlen > 160:
                issues.append(self._issue('meta_desc_long', 'warning',
                                          f'Meta description dài ({dlen} ký tự, nên 150–160)', d[:120], 'long_meta_desc'))
            else:
                issues.append(self._issue('meta_desc_ok', 'pass',
                                          f'Meta description hợp lệ ({dlen} ký tự)', d[:120], None))

        # ─── H1 TAG ──────────────────────────────────────────────────────────────
        h1_tags = soup.find_all('h1')
        if not h1_tags:
            issues.append(self._issue('h1_missing', 'critical',
                                      'Trang thiếu thẻ H1', '', 'missing_h1'))
        elif len(h1_tags) > 1:
            issues.append(self._issue('h1_multiple', 'warning',
                                      f'Có {len(h1_tags)} thẻ H1 (chỉ nên có 1)', '', 'multiple_h1'))
        else:
            issues.append(self._issue('h1_ok', 'pass',
                                      f'H1 tốt: "{h1_tags[0].text.strip()[:60]}"',
                                      h1_tags[0].text.strip(), None))

        # ─── HEADING HIERARCHY ───────────────────────────────────────────────────
        h2s = soup.find_all('h2')
        if h1_tags and not h2s:
            issues.append(self._issue('no_h2', 'warning',
                                      'Không có thẻ H2 nào – cấu trúc nội dung thiếu', '', 'missing_h2'))
        elif h2s:
            issues.append(self._issue('h2_ok', 'pass',
                                      f'Có {len(h2s)} thẻ H2', '', None))

        # ─── IMAGES ALT TEXT ─────────────────────────────────────────────────────
        images = soup.find_all('img')
        missing_alt = [img for img in images if not img.get('alt', '').strip()]
        if images:
            if missing_alt:
                issues.append(self._issue('img_alt_missing', 'warning',
                                          f'{len(missing_alt)}/{len(images)} ảnh thiếu alt text',
                                          ', '.join([img.get('src', '')[:60] for img in missing_alt[:3]]),
                                          'missing_alt'))
            else:
                issues.append(self._issue('img_alt_ok', 'pass',
                                          f'Tất cả {len(images)} ảnh có alt text', '', None))

        # ─── CANONICAL URL ───────────────────────────────────────────────────────
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if not canonical:
            issues.append(self._issue('canonical_missing', 'warning',
                                      'Thiếu thẻ canonical', '', 'missing_canonical'))
        else:
            issues.append(self._issue('canonical_ok', 'pass',
                                      f'Canonical: {canonical.get("href", "")}',
                                      canonical.get('href', ''), None))

        # ─── OPEN GRAPH ──────────────────────────────────────────────────────────
        og_title  = soup.find('meta', property='og:title')
        og_desc   = soup.find('meta', property='og:description')
        og_image  = soup.find('meta', property='og:image')
        missing_og = [tag for tag, el in [('og:title', og_title), ('og:description', og_desc), ('og:image', og_image)] if not el]
        if missing_og:
            issues.append(self._issue('og_incomplete', 'warning',
                                      f'Thiếu Open Graph tags: {", ".join(missing_og)}', '', 'missing_og'))
        else:
            issues.append(self._issue('og_ok', 'pass', 'Open Graph tags đầy đủ', '', None))

        # ─── SCHEMA MARKUP ───────────────────────────────────────────────────────
        schemas = soup.find_all('script', attrs={'type': 'application/ld+json'})
        if not schemas:
            issues.append(self._issue('schema_missing', 'warning',
                                      'Không tìm thấy Schema markup (JSON-LD)', '', 'missing_schema'))
        else:
            issues.append(self._issue('schema_ok', 'pass',
                                      f'Tìm thấy {len(schemas)} khối Schema markup', '', None))

        # ─── VIEWPORT / MOBILE ───────────────────────────────────────────────────
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            issues.append(self._issue('viewport_missing', 'critical',
                                      'Thiếu meta viewport – ảnh hưởng mobile & SEO', '', 'missing_viewport'))
        else:
            issues.append(self._issue('viewport_ok', 'pass',
                                      f'Viewport tag tồn tại: {viewport.get("content", "")}', '', None))

        # ─── WORD COUNT ──────────────────────────────────────────────────────────
        text_content = soup.get_text(separator=' ', strip=True)
        word_count = len(re.findall(r'\b\w+\b', text_content))
        if word_count < 300:
            issues.append(self._issue('thin_content', 'warning',
                                      f'Nội dung mỏng ({word_count} từ, nên > 600)', '', 'thin_content'))
        elif word_count < 600:
            issues.append(self._issue('content_ok_short', 'info',
                                      f'Nội dung đạt mức trung bình ({word_count} từ)', '', None))
        else:
            issues.append(self._issue('content_ok', 'pass',
                                      f'Nội dung đầy đủ ({word_count} từ)', '', None))

        # ─── WORDPRESS SPECIFIC ──────────────────────────────────────────────────
        if self.wp_enabled and html:
            html_lower = html.lower()
            has_rankmath = 'rank-math' in html_lower or 'rankmath' in html_lower
            has_yoast    = 'yoast' in html_lower or 'wpseo' in html_lower

            if has_rankmath:
                issues.append(self._issue('seo_plugin', 'pass',
                                          'Phát hiện Rank Math SEO plugin', 'Rank Math', None))
            elif has_yoast:
                issues.append(self._issue('seo_plugin', 'pass',
                                          'Phát hiện Yoast SEO plugin', 'Yoast', None))
            else:
                issues.append(self._issue('seo_plugin_missing', 'warning',
                                          'Không phát hiện Rank Math hoặc Yoast SEO', '', 'missing_seo_plugin'))

            # Check WordPress version exposure
            if 'wp-content' in html_lower and '?ver=' in html_lower:
                issues.append(self._issue('wp_version_exposed', 'warning',
                                          'WordPress version có thể bị lộ qua ?ver= parameter', '', 'wp_version_exposed'))

        # ─── INTERNAL LINKS ──────────────────────────────────────────────────────
        from urllib.parse import urlparse
        base_domain = urlparse(url).netloc
        all_links = soup.find_all('a', href=True)
        internal_links = [a for a in all_links if base_domain in a['href'] or a['href'].startswith('/')]
        if len(internal_links) < 2:
            issues.append(self._issue('low_internal_links', 'warning',
                                      f'Ít internal links ({len(internal_links)}), nên có ≥ 3', '', 'low_internal_links'))
        else:
            issues.append(self._issue('internal_links_ok', 'pass',
                                      f'Có {len(internal_links)} internal links', '', None))

        return issues

    def _issue(self, check_id, status, message, value, suggestion_key):
        return {
            'check_id': check_id,
            'status': status,       # 'critical', 'warning', 'pass', 'info'
            'message': message,
            'value': str(value)[:200] if value else '',
            'suggestion_key': suggestion_key,
            'category': 'SEO'
        }
