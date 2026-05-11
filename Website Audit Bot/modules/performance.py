"""
Performance Auditor Module
Kiểm tra tốc độ tải trang, Core Web Vitals qua Google PageSpeed API
"""
import time
import requests
from urllib.parse import urlparse


class PerformanceAuditor:
    def __init__(self, config):
        self.config = config
        self.timeout = config.get('request_timeout', 15)
        self.api_key = config.get('pagespeed_api_key', '')
        self.ua = {'User-Agent': config.get('user_agent', 'WebsiteAuditBot/1.0')}

    def audit(self, url):
        issues = []

        # ── Local response time ──────────────────────────────────────────────────
        try:
            start = time.time()
            resp = requests.get(url, headers=self.ua, timeout=self.timeout)
            elapsed_ms = (time.time() - start) * 1000
            status_code = resp.status_code
            page_size_kb = len(resp.content) / 1024

            if elapsed_ms > 3000:
                issues.append(self._issue('slow_response', 'critical',
                    f'Trang tải rất chậm ({elapsed_ms:.0f}ms, nên < 1000ms)',
                    f'{elapsed_ms:.0f}ms', 'slow_page'))
            elif elapsed_ms > 1500:
                issues.append(self._issue('medium_response', 'warning',
                    f'Tốc độ tải trung bình ({elapsed_ms:.0f}ms, nên < 1000ms)',
                    f'{elapsed_ms:.0f}ms', 'slow_page'))
            else:
                issues.append(self._issue('fast_response', 'pass',
                    f'Tốc độ tải tốt ({elapsed_ms:.0f}ms)',
                    f'{elapsed_ms:.0f}ms', None))

            if page_size_kb > 3000:
                issues.append(self._issue('page_too_large', 'warning',
                    f'Kích thước trang lớn ({page_size_kb:.0f} KB, nên < 1000 KB)',
                    f'{page_size_kb:.0f} KB', 'large_page_size'))
            else:
                issues.append(self._issue('page_size_ok', 'pass',
                    f'Kích thước trang hợp lý ({page_size_kb:.0f} KB)',
                    f'{page_size_kb:.0f} KB', None))

        except requests.Timeout:
            issues.append(self._issue('timeout', 'critical',
                f'Trang timeout (>{self.timeout}s)', '', 'slow_page'))
            return issues
        except Exception as e:
            issues.append(self._issue('fetch_error', 'critical',
                f'Lỗi tải trang: {e}', '', None))
            return issues

        # ── Google PageSpeed API ─────────────────────────────────────────────────
        if self.api_key:
            psi_issues = self._check_pagespeed(url)
            issues.extend(psi_issues)
        else:
            issues.append(self._issue('pagespeed_skip', 'info',
                'Chưa cấu hình Google PageSpeed API key – bỏ qua Core Web Vitals',
                'Thêm pagespeed_api_key vào config.json', None))

        return issues

    def _check_pagespeed(self, url):
        issues = []
        try:
            api_url = (
                f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
                f"?url={url}&key={self.api_key}&strategy=mobile"
            )
            r = requests.get(api_url, timeout=30)
            if r.status_code != 200:
                issues.append(self._issue('psi_error', 'info',
                    f'PageSpeed API lỗi {r.status_code}', '', None))
                return issues

            data = r.json()
            cats = data.get('lighthouseResult', {}).get('categories', {})
            metrics = data.get('lighthouseResult', {}).get('audits', {})

            # Overall score
            perf_score = int(cats.get('performance', {}).get('score', 0) * 100)
            if perf_score < 50:
                issues.append(self._issue('psi_score_low', 'critical',
                    f'PageSpeed Score thấp: {perf_score}/100', str(perf_score), 'low_pagespeed'))
            elif perf_score < 80:
                issues.append(self._issue('psi_score_mid', 'warning',
                    f'PageSpeed Score trung bình: {perf_score}/100', str(perf_score), 'low_pagespeed'))
            else:
                issues.append(self._issue('psi_score_ok', 'pass',
                    f'PageSpeed Score tốt: {perf_score}/100', str(perf_score), None))

            # LCP
            lcp = metrics.get('largest-contentful-paint', {})
            lcp_val = lcp.get('displayValue', 'N/A')
            lcp_score = lcp.get('score', 1)
            if lcp_score is not None and lcp_score < 0.5:
                issues.append(self._issue('lcp_bad', 'critical',
                    f'LCP quá chậm: {lcp_val} (nên < 2.5s)', lcp_val, 'bad_lcp'))
            elif lcp_score is not None and lcp_score < 0.9:
                issues.append(self._issue('lcp_warning', 'warning',
                    f'LCP cần cải thiện: {lcp_val}', lcp_val, 'bad_lcp'))
            else:
                issues.append(self._issue('lcp_ok', 'pass', f'LCP tốt: {lcp_val}', lcp_val, None))

            # CLS
            cls = metrics.get('cumulative-layout-shift', {})
            cls_val = cls.get('displayValue', 'N/A')
            cls_score = cls.get('score', 1)
            if cls_score is not None and cls_score < 0.5:
                issues.append(self._issue('cls_bad', 'warning',
                    f'CLS cao: {cls_val} (nên < 0.1)', cls_val, 'bad_cls'))
            else:
                issues.append(self._issue('cls_ok', 'pass', f'CLS tốt: {cls_val}', cls_val, None))

            # FCP
            fcp = metrics.get('first-contentful-paint', {})
            fcp_val = fcp.get('displayValue', 'N/A')
            issues.append(self._issue('fcp_info', 'info', f'FCP: {fcp_val}', fcp_val, None))

        except Exception as e:
            issues.append(self._issue('psi_exception', 'info',
                f'Lỗi PageSpeed API: {e}', '', None))

        return issues

    def _issue(self, check_id, status, message, value, suggestion_key):
        return {
            'check_id': check_id,
            'status': status,
            'message': message,
            'value': str(value)[:200] if value else '',
            'suggestion_key': suggestion_key,
            'category': 'Performance'
        }
