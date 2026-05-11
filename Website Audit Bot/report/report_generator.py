"""
HTML Report Generator - Tạo báo cáo audit đẹp, mở trực tiếp trên browser
"""
import os
import json
import webbrowser
from datetime import datetime
from urllib.parse import urlparse
from report.suggestions import get_suggestion


def generate_report(audit_data, output_dir='reports'):
    """
    audit_data = {
        'url': str,
        'mode': 'single' | 'full',
        'pages': { url: { 'seo': [...], 'performance': [...], 'security': [...], 'links': [...] } },
        'timestamp': datetime
    }
    """
    os.makedirs(output_dir, exist_ok=True)
    domain = urlparse(audit_data['url']).netloc.replace('www.', '').replace('.', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(output_dir, f"audit_{domain}_{timestamp}.html")

    # Collect all issues
    all_issues = []
    for page_url, page_data in audit_data['pages'].items():
        for cat in ['seo', 'performance', 'security', 'links']:
            for issue in page_data.get(cat, []):
                issue['page_url'] = page_url
                all_issues.append(issue)

    # Calculate scores
    scores = _calculate_scores(all_issues)
    overall = int(sum(scores.values()) / len(scores))

    # Build issue cards HTML
    issue_cards_html = _build_issue_cards(all_issues)

    # Build page summary table
    pages_table_html = _build_pages_table(audit_data['pages'])

    html = _build_html(
        target_url=audit_data['url'],
        mode=audit_data['mode'],
        page_count=len(audit_data['pages']),
        timestamp=datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        overall=overall,
        scores=scores,
        all_issues=all_issues,
        issue_cards_html=issue_cards_html,
        pages_table_html=pages_table_html
    )

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    return filename


def _calculate_scores(all_issues):
    cats = {'SEO': [], 'Performance': [], 'Security': [], 'Technical': []}
    for issue in all_issues:
        cat = issue.get('category', 'Technical')
        if cat in cats:
            cats[cat].append(issue['status'])

    scores = {}
    for cat, statuses in cats.items():
        if not statuses:
            scores[cat] = 100
            continue
        total = len(statuses)
        critical = statuses.count('critical') * 20
        warning = statuses.count('warning') * 8
        penalty = min(critical + warning, 100)
        scores[cat] = max(0, 100 - penalty)

    return scores


def _build_issue_cards(all_issues):
    cards = []
    # Group by status priority: critical → warning → info → pass
    order = {'critical': 0, 'warning': 1, 'info': 2, 'pass': 3}
    sorted_issues = sorted(all_issues, key=lambda x: order.get(x['status'], 4))

    for issue in sorted_issues:
        status = issue['status']
        if status == 'pass':
            continue  # Pass issues shown in summary only

        suggestion = get_suggestion(issue.get('suggestion_key', '')) if issue.get('suggestion_key') else None

        badge_class = {'critical': 'badge-critical', 'warning': 'badge-warning',
                       'info': 'badge-info'}.get(status, 'badge-info')
        icon = {'critical': '🔴', 'warning': '🟡', 'info': 'ℹ️'}.get(status, '✅')

        suggestion_html = ''
        if suggestion:
            steps_html = ''.join(f'<li>{s}</li>' for s in suggestion['steps'])
            wp_html = f'<div class="wp-tip"><span class="wp-icon">🔧 WordPress Tip:</span> {suggestion["wp_tip"]}</div>' if suggestion.get('wp_tip') else ''
            suggestion_html = f'''
            <button class="fix-btn" onclick="toggleFix(this)">💡 Hướng dẫn sửa lỗi</button>
            <div class="fix-guide" style="display:none">
                <div class="fix-why"><strong>❓ Tại sao?</strong> {suggestion["why"]}</div>
                <div class="fix-steps"><strong>📋 Cách sửa:</strong><ol>{steps_html}</ol></div>
                {wp_html}
            </div>'''

        value_html = f'<div class="issue-value">{issue["value"][:150]}</div>' if issue.get('value') else ''
        cat_tag = f'<span class="cat-tag cat-{issue.get("category","").lower()}">{issue.get("category","")}</span>'
        page_tag = f'<span class="page-tag">{issue.get("page_url","")[:60]}</span>' if issue.get("page_url") else ''

        cards.append(f'''
        <div class="issue-card {badge_class}">
            <div class="issue-header">
                <span class="issue-icon">{icon}</span>
                <div class="issue-meta">
                    <div class="issue-msg">{issue["message"]}</div>
                    <div class="issue-tags">{cat_tag} {page_tag}</div>
                </div>
                <span class="issue-badge {badge_class}">{status.upper()}</span>
            </div>
            {value_html}
            {suggestion_html}
        </div>''')

    return '\n'.join(cards) if cards else '<p class="no-issues">✅ Không có vấn đề nghiêm trọng nào!</p>'


def _build_pages_table(pages):
    rows = []
    for url, data in list(pages.items())[:50]:
        seo_issues = [i for i in data.get('seo', []) if i['status'] in ('critical', 'warning')]
        perf_issues = [i for i in data.get('performance', []) if i['status'] in ('critical', 'warning')]
        sec_issues = [i for i in data.get('security', []) if i['status'] in ('critical', 'warning')]
        total = len(seo_issues) + len(perf_issues) + len(sec_issues)
        status_color = '#ef4444' if total > 5 else '#f59e0b' if total > 2 else '#10b981'
        rows.append(f'''<tr>
            <td><a href="{url}" target="_blank" class="page-link">{url[:70]}</a></td>
            <td style="color:#60a5fa">{len(seo_issues)}</td>
            <td style="color:#f59e0b">{len(perf_issues)}</td>
            <td style="color:#ef4444">{len(sec_issues)}</td>
            <td><span style="color:{status_color};font-weight:700">{total} issues</span></td>
        </tr>''')
    return '\n'.join(rows)


def _score_color(score):
    if score >= 80: return '#10b981'
    if score >= 60: return '#f59e0b'
    return '#ef4444'


def _score_class(score):
    if score >= 80: return 'score-good'
    if score >= 60: return 'score-mid'
    return 'score-bad'


def _count_by_status(all_issues, status):
    return sum(1 for i in all_issues if i['status'] == status)


def _build_html(target_url, mode, page_count, timestamp, overall, scores, all_issues, issue_cards_html, pages_table_html):
    critical_count = _count_by_status(all_issues, 'critical')
    warning_count = _count_by_status(all_issues, 'warning')
    pass_count = _count_by_status(all_issues, 'pass')
    overall_color = _score_color(overall)
    score_cat_cards = ''.join(f'''
        <div class="cat-score-card">
            <div class="cat-score-num" style="color:{_score_color(v)}">{v}</div>
            <div class="cat-score-label">{k}</div>
            <div class="cat-score-bar">
                <div class="cat-score-fill" style="width:{v}%;background:{_score_color(v)}"></div>
            </div>
        </div>''' for k, v in scores.items())

    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Website Audit Report – {target_url}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0d1117; --surface: #161b22; --surface2: #1c2128; --surface3: #21262d;
    --border: #30363d; --text: #e6edf3; --text-muted: #8b949e; --accent: #58a6ff;
    --critical: #ef4444; --warning: #f59e0b; --pass: #10b981; --info: #6366f1;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:'Inter',sans-serif; background:var(--bg); color:var(--text); min-height:100vh; }}

  /* ── Header ── */
  .header {{ background:linear-gradient(135deg,#0d1117 0%,#1a1f2e 50%,#0d1117 100%);
    border-bottom:1px solid var(--border); padding:32px 40px; position:relative; overflow:hidden; }}
  .header::before {{ content:''; position:absolute; top:-50%; left:-50%; width:200%; height:200%;
    background:radial-gradient(ellipse at center,rgba(88,166,255,0.08) 0%,transparent 60%);
    pointer-events:none; }}
  .header-top {{ display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px; }}
  .brand {{ display:flex; align-items:center; gap:12px; }}
  .brand-icon {{ width:44px; height:44px; background:linear-gradient(135deg,#58a6ff,#7c3aed);
    border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:22px; }}
  .brand-text h1 {{ font-size:22px; font-weight:800; color:var(--text); }}
  .brand-text p {{ font-size:13px; color:var(--text-muted); margin-top:2px; }}
  .header-meta {{ text-align:right; }}
  .header-meta .target-url {{ font-size:18px; font-weight:700; color:var(--accent); word-break:break-all; }}
  .header-meta .meta-info {{ font-size:12px; color:var(--text-muted); margin-top:4px; }}
  .mode-badge {{ display:inline-block; padding:3px 10px; border-radius:20px; font-size:11px;
    font-weight:600; background:rgba(88,166,255,0.15); color:var(--accent); border:1px solid rgba(88,166,255,0.3); }}

  /* ── Main Layout ── */
  .container {{ max-width:1200px; margin:0 auto; padding:32px 24px; }}

  /* ── Score Hero ── */
  .score-hero {{ display:grid; grid-template-columns:200px 1fr; gap:32px;
    background:var(--surface); border:1px solid var(--border); border-radius:16px;
    padding:32px; margin-bottom:28px; align-items:center; }}
  .score-circle {{ text-align:center; }}
  .score-num {{ font-size:72px; font-weight:800; line-height:1; color:{overall_color}; }}
  .score-label {{ font-size:13px; color:var(--text-muted); margin-top:6px; font-weight:500; }}
  .score-right h2 {{ font-size:18px; font-weight:700; margin-bottom:20px; }}
  .cat-scores {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }}
  .cat-score-card {{ background:var(--surface2); border-radius:12px; padding:16px; text-align:center; border:1px solid var(--border); }}
  .cat-score-num {{ font-size:32px; font-weight:800; }}
  .cat-score-label {{ font-size:11px; color:var(--text-muted); font-weight:600; margin:4px 0 8px; text-transform:uppercase; letter-spacing:0.5px; }}
  .cat-score-bar {{ height:4px; background:var(--surface3); border-radius:2px; overflow:hidden; }}
  .cat-score-fill {{ height:100%; border-radius:2px; transition:width 1s ease; }}

  /* ── Stats Row ── */
  .stats-row {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:28px; }}
  .stat-card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px;
    padding:20px; display:flex; align-items:center; gap:16px; }}
  .stat-icon {{ width:48px; height:48px; border-radius:12px; display:flex; align-items:center;
    justify-content:center; font-size:22px; flex-shrink:0; }}
  .stat-icon.critical {{ background:rgba(239,68,68,0.15); }}
  .stat-icon.warning {{ background:rgba(245,158,11,0.15); }}
  .stat-icon.pass {{ background:rgba(16,185,129,0.15); }}
  .stat-value {{ font-size:32px; font-weight:800; }}
  .stat-value.critical {{ color:var(--critical); }}
  .stat-value.warning {{ color:var(--warning); }}
  .stat-value.pass {{ color:var(--pass); }}
  .stat-label {{ font-size:13px; color:var(--text-muted); margin-top:2px; }}

  /* ── Section ── */
  .section {{ margin-bottom:32px; }}
  .section-title {{ font-size:16px; font-weight:700; margin-bottom:16px;
    display:flex; align-items:center; gap:8px; color:var(--text); }}
  .section-title::after {{ content:''; flex:1; height:1px; background:var(--border); margin-left:12px; }}

  /* ── Issue Cards ── */
  .issue-card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px;
    padding:18px; margin-bottom:10px; transition:border-color 0.2s; }}
  .issue-card:hover {{ border-color:var(--accent); }}
  .issue-card.badge-critical {{ border-left:3px solid var(--critical); }}
  .issue-card.badge-warning {{ border-left:3px solid var(--warning); }}
  .issue-card.badge-info {{ border-left:3px solid var(--info); }}
  .issue-header {{ display:flex; align-items:flex-start; gap:12px; }}
  .issue-icon {{ font-size:18px; flex-shrink:0; margin-top:1px; }}
  .issue-meta {{ flex:1; }}
  .issue-msg {{ font-size:14px; font-weight:600; color:var(--text); }}
  .issue-tags {{ display:flex; gap:6px; margin-top:6px; flex-wrap:wrap; }}
  .cat-tag {{ padding:2px 8px; border-radius:4px; font-size:11px; font-weight:600; }}
  .cat-seo {{ background:rgba(88,166,255,0.15); color:#58a6ff; }}
  .cat-security {{ background:rgba(239,68,68,0.15); color:#ef4444; }}
  .cat-performance {{ background:rgba(245,158,11,0.15); color:#f59e0b; }}
  .cat-technical {{ background:rgba(99,102,241,0.15); color:#818cf8; }}
  .page-tag {{ font-size:11px; color:var(--text-muted); }}
  .issue-badge {{ padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700;
    flex-shrink:0; align-self:flex-start; }}
  .badge-critical {{ background:rgba(239,68,68,0.15); color:var(--critical); }}
  .badge-warning {{ background:rgba(245,158,11,0.15); color:var(--warning); }}
  .badge-info {{ background:rgba(99,102,241,0.15); color:var(--info); }}
  .issue-value {{ margin-top:8px; font-size:12px; color:var(--text-muted);
    background:var(--surface2); border-radius:6px; padding:8px 12px;
    font-family:monospace; word-break:break-all; max-height:60px; overflow:hidden; }}

  /* ── Fix Guide ── */
  .fix-btn {{ margin-top:12px; background:linear-gradient(135deg,rgba(88,166,255,0.1),rgba(124,58,237,0.1));
    color:var(--accent); border:1px solid rgba(88,166,255,0.3); border-radius:8px;
    padding:7px 14px; font-size:12px; font-weight:600; cursor:pointer;
    transition:all 0.2s; font-family:inherit; }}
  .fix-btn:hover {{ background:rgba(88,166,255,0.2); border-color:var(--accent); }}
  .fix-guide {{ margin-top:12px; background:var(--surface2); border-radius:10px;
    padding:16px; border:1px solid var(--border); animation:fadeIn 0.2s ease; }}
  @keyframes fadeIn {{ from{{opacity:0;transform:translateY(-4px)}} to{{opacity:1;transform:translateY(0)}} }}
  .fix-why {{ font-size:13px; color:var(--text-muted); margin-bottom:12px; line-height:1.6; }}
  .fix-steps {{ font-size:13px; color:var(--text); }}
  .fix-steps ol {{ padding-left:18px; margin-top:8px; }}
  .fix-steps li {{ margin-bottom:6px; line-height:1.6; }}
  .wp-tip {{ margin-top:12px; background:rgba(88,166,255,0.08); border:1px solid rgba(88,166,255,0.2);
    border-radius:8px; padding:10px 14px; font-size:12px; color:var(--accent); }}
  .wp-icon {{ font-weight:700; margin-right:4px; }}

  /* ── Pages Table ── */
  .pages-table {{ width:100%; border-collapse:collapse; background:var(--surface);
    border-radius:12px; overflow:hidden; border:1px solid var(--border); }}
  .pages-table th {{ background:var(--surface2); padding:12px 16px; font-size:12px;
    font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:var(--text-muted);
    text-align:left; }}
  .pages-table td {{ padding:12px 16px; font-size:13px; border-top:1px solid var(--border); }}
  .pages-table tr:hover td {{ background:var(--surface2); }}
  .page-link {{ color:var(--accent); text-decoration:none; font-size:12px; }}
  .page-link:hover {{ text-decoration:underline; }}
  .no-issues {{ text-align:center; color:var(--pass); font-size:16px; padding:40px; }}

  /* ── Filter Tabs ── */
  .filter-tabs {{ display:flex; gap:8px; margin-bottom:16px; flex-wrap:wrap; }}
  .filter-tab {{ padding:6px 14px; border-radius:20px; font-size:12px; font-weight:600;
    cursor:pointer; border:1px solid var(--border); background:var(--surface2);
    color:var(--text-muted); transition:all 0.2s; font-family:inherit; }}
  .filter-tab:hover, .filter-tab.active {{ background:var(--accent); color:#fff; border-color:var(--accent); }}

  /* ── Footer ── */
  .footer {{ text-align:center; padding:32px; color:var(--text-muted); font-size:12px;
    border-top:1px solid var(--border); margin-top:48px; }}
  .footer a {{ color:var(--accent); text-decoration:none; }}

  @media(max-width:768px) {{
    .score-hero {{ grid-template-columns:1fr; }}
    .cat-scores {{ grid-template-columns:repeat(2,1fr); }}
    .stats-row {{ grid-template-columns:1fr; }}
    .header {{ padding:20px; }}
    .container {{ padding:20px 16px; }}
  }}
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <div class="header-top">
    <div class="brand">
      <div class="brand-icon">🔍</div>
      <div class="brand-text">
        <h1>Website Audit Bot</h1>
        <p>Powered by Antigravity AI Tools</p>
      </div>
    </div>
    <div class="header-meta">
      <div class="target-url">{target_url}</div>
      <div class="meta-info">
        <span class="mode-badge">{'🔎 Single Page' if mode == 'single' else '🕷️ Full Crawl'}</span>
        &nbsp; {page_count} trang được quét &nbsp;·&nbsp; {timestamp}
      </div>
    </div>
  </div>
</div>

<div class="container">

  <!-- SCORE HERO -->
  <div class="score-hero">
    <div class="score-circle">
      <div class="score-num" style="color:{overall_color}">{overall}</div>
      <div class="score-label">/ 100<br>Overall Score</div>
    </div>
    <div class="score-right">
      <h2>📊 Điểm số theo danh mục</h2>
      <div class="cat-scores">{score_cat_cards}</div>
    </div>
  </div>

  <!-- STATS -->
  <div class="stats-row">
    <div class="stat-card">
      <div class="stat-icon critical">🔴</div>
      <div>
        <div class="stat-value critical">{critical_count}</div>
        <div class="stat-label">Lỗi nghiêm trọng (Critical)</div>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon warning">⚠️</div>
      <div>
        <div class="stat-value warning">{warning_count}</div>
        <div class="stat-label">Cảnh báo (Warning)</div>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon pass">✅</div>
      <div>
        <div class="stat-value pass">{pass_count}</div>
        <div class="stat-label">Kiểm tra đạt (Passed)</div>
      </div>
    </div>
  </div>

  <!-- ISSUES -->
  <div class="section">
    <div class="section-title">⚠️ Vấn đề tìm thấy</div>
    <div class="filter-tabs">
      <button class="filter-tab active" onclick="filterIssues('all', this)">Tất cả</button>
      <button class="filter-tab" onclick="filterIssues('badge-critical', this)">🔴 Critical</button>
      <button class="filter-tab" onclick="filterIssues('badge-warning', this)">🟡 Warning</button>
      <button class="filter-tab" onclick="filterIssues('cat-seo', this)">SEO</button>
      <button class="filter-tab" onclick="filterIssues('cat-security', this)">Security</button>
      <button class="filter-tab" onclick="filterIssues('cat-performance', this)">Performance</button>
      <button class="filter-tab" onclick="filterIssues('cat-technical', this)">Technical</button>
    </div>
    <div id="issues-container">
      {issue_cards_html}
    </div>
  </div>

  <!-- PAGES TABLE -->
  <div class="section">
    <div class="section-title">🗺️ Danh sách trang đã quét</div>
    <table class="pages-table">
      <thead><tr><th>URL</th><th>SEO Issues</th><th>Perf Issues</th><th>Sec Issues</th><th>Tổng</th></tr></thead>
      <tbody>{pages_table_html}</tbody>
    </table>
  </div>

</div>

<!-- FOOTER -->
<div class="footer">
  <p>Báo cáo được tạo bởi <strong>Website Audit Bot</strong> · {timestamp}</p>
  <p style="margin-top:6px">Kiểm tra lại tại: <a href="https://pagespeed.web.dev" target="_blank">PageSpeed Insights</a> · 
  <a href="https://search.google.com/test/rich-results" target="_blank">Rich Results Test</a> · 
  <a href="https://www.ssllabs.com/ssltest/" target="_blank">SSL Labs</a></p>
</div>

<script>
function toggleFix(btn) {{
  const guide = btn.nextElementSibling;
  if (guide.style.display === 'none') {{
    guide.style.display = 'block';
    btn.textContent = '🔼 Ẩn hướng dẫn';
  }} else {{
    guide.style.display = 'none';
    btn.textContent = '💡 Hướng dẫn sửa lỗi';
  }}
}}

function filterIssues(cls, btn) {{
  document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  const cards = document.querySelectorAll('.issue-card');
  cards.forEach(card => {{
    if (cls === 'all') {{
      card.style.display = '';
    }} else if (cls.startsWith('cat-')) {{
      const hasCat = card.querySelector('.' + cls);
      card.style.display = hasCat ? '' : 'none';
    }} else {{
      card.style.display = card.classList.contains(cls) ? '' : 'none';
    }}
  }});
}}

// Animate score bars on load
window.addEventListener('load', () => {{
  document.querySelectorAll('.cat-score-fill').forEach(bar => {{
    const w = bar.style.width;
    bar.style.width = '0';
    setTimeout(() => {{ bar.style.width = w; }}, 100);
  }});
}});
</script>
</body>
</html>'''
