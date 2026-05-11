"""
Website Crawler Module - Crawl toàn bộ site hoặc single page
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn


class WebCrawler:
    def __init__(self, config):
        self.config = config
        self.timeout = config.get('request_timeout', 15)
        self.max_pages = config.get('max_pages', 50)
        self.max_depth = config.get('crawl_depth', 3)
        self.ua = {'User-Agent': config.get('user_agent', 'WebsiteAuditBot/1.0')}

    def crawl(self, start_url, max_pages=None, progress_callback=None):
        """
        Crawl toàn bộ website bắt đầu từ start_url.
        Trả về dict: {url: {'html': ..., 'soup': ..., 'status': ..., 'depth': ...}}
        """
        if max_pages is None:
            max_pages = self.max_pages

        parsed_start = urlparse(start_url)
        base_domain = parsed_start.netloc
        base_scheme = parsed_start.scheme

        visited = {}
        queue = deque([(start_url, 0)])
        seen = {start_url}

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]Đang crawl:[/] [yellow]{task.description}"),
            BarColumn(),
            TextColumn("[green]{task.completed}/{task.total} trang"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("crawling", total=max_pages)

            while queue and len(visited) < max_pages:
                url, depth = queue.popleft()

                if depth > self.max_depth:
                    continue

                try:
                    resp = requests.get(url, headers=self.ua, timeout=self.timeout, allow_redirects=True)
                    content_type = resp.headers.get('content-type', '')

                    if 'text/html' not in content_type:
                        continue

                    soup = BeautifulSoup(resp.text, 'html.parser')
                    visited[url] = {
                        'html': resp.text,
                        'soup': soup,
                        'status': resp.status_code,
                        'depth': depth,
                        'size_kb': len(resp.content) / 1024,
                        'response_ms': resp.elapsed.total_seconds() * 1000
                    }

                    progress.update(task, completed=len(visited),
                                    description=f"{url[:60]}...")

                    # Discover links
                    if depth < self.max_depth:
                        for a in soup.find_all('a', href=True):
                            href = a['href'].strip()
                            if not href or href.startswith('#') or href.startswith('mailto:'):
                                continue
                            full_url = urljoin(url, href)
                            fp = urlparse(full_url)
                            # Only follow same-domain links
                            if fp.netloc == base_domain and full_url not in seen:
                                seen.add(full_url)
                                clean_url = f"{fp.scheme}://{fp.netloc}{fp.path}"
                                if clean_url not in seen:
                                    seen.add(clean_url)
                                    queue.append((clean_url, depth + 1))

                except Exception as e:
                    visited[url] = {
                        'html': '',
                        'soup': None,
                        'status': 0,
                        'depth': depth,
                        'size_kb': 0,
                        'response_ms': 0,
                        'error': str(e)
                    }

        return visited

    def fetch_single(self, url):
        """Lấy HTML của một trang duy nhất"""
        try:
            resp = requests.get(url, headers=self.ua, timeout=self.timeout, allow_redirects=True)
            soup = BeautifulSoup(resp.text, 'html.parser')
            return {
                url: {
                    'html': resp.text,
                    'soup': soup,
                    'status': resp.status_code,
                    'depth': 0,
                    'size_kb': len(resp.content) / 1024,
                    'response_ms': resp.elapsed.total_seconds() * 1000
                }
            }
        except Exception as e:
            return {url: {'html': '', 'soup': None, 'status': 0, 'depth': 0,
                          'size_kb': 0, 'response_ms': 0, 'error': str(e)}}
