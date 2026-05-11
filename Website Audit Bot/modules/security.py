"""
Security Auditor Module - Kiểm tra SSL, headers, robots.txt, sitemap
"""
import ssl
import socket
import datetime
import requests
from urllib.parse import urljoin, urlparse


class SecurityAuditor:
    def __init__(self, config):
        self.config = config
        self.timeout = config.get('request_timeout', 15)
        self.ua = {'User-Agent': config.get('user_agent', 'WebsiteAuditBot/1.0')}

    def audit(self, url):
        issues = []
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        # HTTPS / SSL
        if parsed.scheme != 'https':
            issues.append(self._issue('no_https', 'critical',
                'Trang không dùng HTTPS', parsed.scheme, 'no_https'))
        else:
            issues.extend(self._check_ssl(parsed.netloc))

        # Security Headers
        try:
            resp = requests.get(url, headers=self.ua, timeout=self.timeout, allow_redirects=True)
            issues.extend(self._check_headers(resp.headers))
            if parsed.scheme == 'https' and 'http://' in resp.text:
                issues.append(self._issue('mixed_content', 'warning',
                    'Phát hiện mixed content (HTTP resources trên HTTPS)', '', 'mixed_content'))
            else:
                issues.append(self._issue('no_mixed_content', 'pass',
                    'Không phát hiện mixed content', '', None))
        except Exception as e:
            issues.append(self._issue('header_fail', 'info', f'Lỗi kiểm tra headers: {e}', '', None))

        # Robots.txt
        try:
            r = requests.get(urljoin(base_url, '/robots.txt'), headers=self.ua, timeout=self.timeout)
            if r.status_code == 200 and len(r.text) > 10:
                issues.append(self._issue('robots_ok', 'pass',
                    f'robots.txt tồn tại ({len(r.text)} bytes)', '', None))
            else:
                issues.append(self._issue('robots_missing', 'warning',
                    'Không tìm thấy robots.txt', '', 'missing_robots'))
        except Exception:
            issues.append(self._issue('robots_error', 'warning',
                'Không truy cập được robots.txt', '', 'missing_robots'))

        # Sitemap.xml
        sitemap_found = False
        for path in ['/sitemap.xml', '/sitemap_index.xml', '/wp-sitemap.xml']:
            try:
                r = requests.get(urljoin(base_url, path), headers=self.ua, timeout=self.timeout)
                if r.status_code == 200 and ('<url' in r.text or '<sitemap' in r.text):
                    issues.append(self._issue('sitemap_ok', 'pass',
                        f'Sitemap tìm thấy: {path}', urljoin(base_url, path), None))
                    sitemap_found = True
                    break
            except Exception:
                pass
        if not sitemap_found:
            issues.append(self._issue('sitemap_missing', 'warning',
                'Không tìm thấy sitemap.xml', '', 'missing_sitemap'))

        return issues

    def _check_ssl(self, hostname):
        issues = []
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
                s.settimeout(10)
                s.connect((hostname, 443))
                cert = s.getpeercert()
            expire_str = cert.get('notAfter', '')
            if expire_str:
                expire_date = datetime.datetime.strptime(expire_str, '%b %d %H:%M:%S %Y %Z')
                days = (expire_date - datetime.datetime.utcnow()).days
                if days < 0:
                    issues.append(self._issue('ssl_expired', 'critical',
                        f'SSL đã hết hạn {abs(days)} ngày trước!', expire_str, 'ssl_expired'))
                elif days < 30:
                    issues.append(self._issue('ssl_expiring', 'warning',
                        f'SSL sắp hết hạn sau {days} ngày', expire_str, 'ssl_expiring'))
                else:
                    issues.append(self._issue('ssl_ok', 'pass',
                        f'SSL hợp lệ, còn {days} ngày', expire_str, None))
        except ssl.SSLCertVerificationError:
            issues.append(self._issue('ssl_invalid', 'critical',
                'SSL certificate không hợp lệ', '', 'ssl_invalid'))
        except Exception as e:
            issues.append(self._issue('ssl_error', 'info',
                f'Không kiểm tra được SSL: {e}', '', None))
        return issues

    def _check_headers(self, headers):
        issues = []
        header_keys = {k.lower() for k in headers}
        important = [
            ('x-frame-options',           'xframe_missing',   'Thiếu X-Frame-Options (chống clickjacking)',     'missing_xframe'),
            ('x-content-type-options',    'xcto_missing',     'Thiếu X-Content-Type-Options header',            'missing_xcto'),
            ('strict-transport-security', 'hsts_missing',     'Thiếu HSTS (Strict-Transport-Security)',         'missing_hsts'),
            ('referrer-policy',           'referrer_missing', 'Thiếu Referrer-Policy header',                   'missing_referrer'),
            ('content-security-policy',   'csp_missing',      'Thiếu Content-Security-Policy (CSP)',            'missing_csp'),
        ]
        for hname, check_id, msg, skey in important:
            if hname not in header_keys:
                issues.append(self._issue(check_id, 'warning', msg, '', skey))
            else:
                issues.append(self._issue(f'{check_id}_ok', 'pass', f'{hname} tồn tại', '', None))
        return issues

    def _issue(self, check_id, status, message, value, suggestion_key):
        return {
            'check_id': check_id,
            'status': status,
            'message': message,
            'value': str(value)[:200] if value else '',
            'suggestion_key': suggestion_key,
            'category': 'Security'
        }
