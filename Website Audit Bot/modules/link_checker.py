"""
Link Checker Module - Kiểm tra broken links và redirect chains
"""
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


class LinkChecker:
    def __init__(self, config):
        self.config = config
        self.timeout = config.get('request_timeout', 15)
        self.workers = min(config.get('concurrent_requests', 5), 10)
        self.ua = {'User-Agent': config.get('user_agent', 'WebsiteAuditBot/1.0')}

    def check_page(self, url, soup=None):
        """Kiểm tra tất cả links trên một trang"""
        issues = []

        if soup is None:
            try:
                resp = requests.get(url, headers=self.ua, timeout=self.timeout)
                soup = BeautifulSoup(resp.text, 'html.parser')
            except Exception as e:
                return [self._issue('fetch_error', 'critical', f'Lỗi tải trang: {e}', url, None)]

        base = urlparse(url)
        base_domain = base.netloc
        all_links = soup.find_all('a', href=True)

        link_urls = []
        for a in all_links:
            href = a['href'].strip()
            if href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                continue
            full_url = urljoin(url, href)
            link_urls.append((a.text.strip()[:50] or href[:50], full_url))

        if not link_urls:
            issues.append(self._issue('no_links', 'info', 'Không tìm thấy links trên trang', '', None))
            return issues

        issues.append(self._issue('link_count', 'info',
            f'Tổng số {len(link_urls)} links cần kiểm tra', '', None))

        # Check links in parallel
        broken, redirects, ok = [], [], []
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_map = {executor.submit(self._check_link, link_url): anchor
                          for anchor, link_url in link_urls}
            for future in as_completed(future_map):
                anchor = future_map[future]
                try:
                    status_code, final_url, redirect_count, link_url = future.result()
                    if status_code in (404, 410):
                        broken.append({'anchor': anchor, 'url': link_url, 'status': status_code})
                    elif redirect_count > 2:
                        redirects.append({'anchor': anchor, 'url': link_url,
                                          'final': final_url, 'hops': redirect_count})
                    else:
                        ok.append(link_url)
                except Exception:
                    pass

        if broken:
            issues.append(self._issue('broken_links', 'critical',
                f'{len(broken)} broken link(s) tìm thấy',
                '\n'.join([f"{b["url"]} [{b["status"]}]" for b in broken[:5]]),
                'broken_links'))
        else:
            issues.append(self._issue('no_broken', 'pass',
                f'Không có broken links trong {len(ok)} links đã kiểm tra', '', None))

        if redirects:
            issues.append(self._issue('redirect_chains', 'warning',
                f'{len(redirects)} links có redirect chain dài (> 2 bước)',
                '\n'.join([f"{r["url"]} → {r["hops"]} hops" for r in redirects[:3]]),
                'redirect_chains'))
        elif len(ok) > 0:
            issues.append(self._issue('no_redirects', 'pass',
                'Không có redirect chain dài bất thường', '', None))

        return issues

    def _check_link(self, url):
        try:
            history = []
            resp = requests.get(url, headers=self.ua, timeout=self.timeout,
                                allow_redirects=True)
            redirect_count = len(resp.history)
            final_url = resp.url
            return (resp.status_code, final_url, redirect_count, url)
        except Exception:
            return (0, url, 0, url)

    def _issue(self, check_id, status, message, value, suggestion_key):
        return {
            'check_id': check_id,
            'status': status,
            'message': message,
            'value': str(value)[:500] if value else '',
            'suggestion_key': suggestion_key,
            'category': 'Technical'
        }
