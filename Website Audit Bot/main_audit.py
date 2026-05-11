"""
Website Audit Bot - Main Entry Point
Chạy: python main_audit.py
"""
import os
import sys
import json
import webbrowser
import re
from datetime import datetime
from urllib.parse import urlparse

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from modules.crawler import WebCrawler
from modules.seo_auditor import SEOAuditor
from modules.performance import PerformanceAuditor
from modules.security import SecurityAuditor
from modules.link_checker import LinkChecker
from report.report_generator import generate_report

console = Console()

BANNER = """
[bold cyan]
 ██╗    ██╗███████╗██████╗ ███████╗██╗████████╗███████╗
 ██║    ██║██╔════╝██╔══██╗██╔════╝██║╚══██╔══╝██╔════╝
 ██║ █╗ ██║█████╗  ██████╔╝███████╗██║   ██║   █████╗  
 ██║███╗██║██╔══╝  ██╔══██╗╚════██║██║   ██║   ██╔══╝  
 ╚███╔███╔╝███████╗██████╔╝███████║██║   ██║   ███████╗
  ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝╚═╝   ╚═╝   ╚══════╝[/bold cyan]
[bold white]         AUDIT BOT – WordPress SEO & Security Scanner[/bold white]
[dim]         Kiểm tra SEO · Hiệu suất · Bảo mật · Kỹ thuật[/dim]
"""


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if not os.path.exists(config_path):
        console.print("[yellow]⚠️  Không tìm thấy config.json – dùng cấu hình mặc định[/yellow]")
        return {}
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_url(url):
    if not url.startswith('http'):
        url = 'https://' + url
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None
        return url
    except Exception:
        return None


def print_summary(all_issues, page_count):
    critical = [i for i in all_issues if i['status'] == 'critical']
    warning  = [i for i in all_issues if i['status'] == 'warning']
    passed   = [i for i in all_issues if i['status'] == 'pass']

    table = Table(title=f"📊 Tóm tắt kết quả – {page_count} trang", 
                  border_style="blue", show_header=True, header_style="bold cyan")
    table.add_column("Mức độ", style="bold", width=15)
    table.add_column("Số lượng", justify="center", width=12)
    table.add_column("Mô tả", style="dim")

    table.add_row("🔴 CRITICAL", f"[bold red]{len(critical)}[/bold red]",
                  "Lỗi nghiêm trọng cần xử lý ngay")
    table.add_row("🟡 WARNING",  f"[bold yellow]{len(warning)}[/bold yellow]",
                  "Cảnh báo cần cải thiện")
    table.add_row("✅ PASSED",   f"[bold green]{len(passed)}[/bold green]",
                  "Kiểm tra đạt yêu cầu")

    console.print()
    console.print(table)

    if critical:
        console.print("\n[bold red]🚨 Top 5 lỗi nghiêm trọng nhất:[/bold red]")
        for issue in critical[:5]:
            console.print(f"  [red]•[/red] [{issue.get('category','?')}] {issue['message']}")

    if warning:
        console.print("\n[bold yellow]⚠️  Top 5 cảnh báo:[/bold yellow]")
        for issue in warning[:5]:
            console.print(f"  [yellow]•[/yellow] [{issue.get('category','?')}] {issue['message']}")


def run_audit_on_pages(pages, config):
    """Chạy tất cả audit modules trên danh sách pages"""
    seo_auditor  = SEOAuditor(config)
    perf_auditor = PerformanceAuditor(config)
    sec_auditor  = SecurityAuditor(config)
    link_checker = LinkChecker(config)

    results = {}
    total = len(pages)

    with console.status("[bold cyan]Đang phân tích...[/bold cyan]") as status:
        for idx, (url, page_data) in enumerate(pages.items(), 1):
            status.update(f"[cyan]({idx}/{total}) Phân tích: {url[:60]}...[/cyan]")

            soup = page_data.get('soup')
            html = page_data.get('html', '')

            results[url] = {
                'seo':         seo_auditor.audit_page(url, html=html, soup=soup) if soup else [],
                'performance': perf_auditor.audit(url),
                'security':    sec_auditor.audit(url) if idx == 1 else [],  # Security chỉ check trang chủ
                'links':       link_checker.check_page(url, soup=soup) if soup else [],
            }

    return results


def main():
    console.print(BANNER)
    config = load_config()

    # ── Chọn chế độ ──────────────────────────────────────────────
    console.print(Panel(
        "[bold]Chọn chế độ kiểm tra:[/bold]\n\n"
        "  [cyan][1][/cyan] 🔎 Single Page Audit – Kiểm tra một trang cụ thể\n"
        "  [cyan][2][/cyan] 🕷️  Full Site Crawl  – Crawl và kiểm tra toàn bộ website\n"
        "  [cyan][3][/cyan] ❌ Thoát",
        border_style="cyan", title="Website Audit Bot", expand=False
    ))

    mode_choice = Prompt.ask("[bold cyan]Nhập lựa chọn[/bold cyan]", choices=["1", "2", "3"], default="1")

    if mode_choice == "3":
        console.print("[yellow]👋 Tạm biệt![/yellow]")
        sys.exit(0)

    # ── Nhập URL ──────────────────────────────────────────────────
    default_url = config.get('target_url', 'https://example.com')
    raw_url = Prompt.ask(f"\n[bold]🌐 Nhập URL website[/bold]", default=default_url)
    url = validate_url(raw_url)

    if not url:
        console.print("[red]❌ URL không hợp lệ. Vui lòng thử lại.[/red]")
        sys.exit(1)

    console.print(f"\n[green]✔️  URL:[/green] [bold]{url}[/bold]")

    # ── Cấu hình crawl ───────────────────────────────────────────
    mode = 'single' if mode_choice == '1' else 'full'
    crawler = WebCrawler(config)

    if mode == 'full':
        max_pages = IntPrompt.ask(
            "[bold]📄 Số trang tối đa cần crawl[/bold]",
            default=config.get('max_pages', 30)
        )
        config['max_pages'] = max_pages
        console.print(f"\n[cyan]🕷️  Bắt đầu crawl tối đa {max_pages} trang...[/cyan]\n")
        pages = crawler.crawl(url, max_pages=max_pages)
    else:
        console.print(f"\n[cyan]🔎 Đang tải trang...[/cyan]")
        pages = crawler.fetch_single(url)

    if not pages:
        console.print("[red]❌ Không thể tải trang. Kiểm tra lại URL và kết nối mạng.[/red]")
        sys.exit(1)

    console.print(f"[green]✅ Đã tải {len(pages)} trang[/green]\n")

    # ── Chạy audit ───────────────────────────────────────────────
    console.print("[bold cyan]🔍 Đang chạy kiểm tra...[/bold cyan]\n")
    page_results = run_audit_on_pages(pages, config)

    # ── Tổng hợp issues ──────────────────────────────────────────
    all_issues = []
    for page_url, cats in page_results.items():
        for cat_issues in cats.values():
            for issue in cat_issues:
                issue['page_url'] = page_url
                all_issues.append(issue)

    print_summary(all_issues, len(pages))

    # ── Tạo báo cáo HTML ─────────────────────────────────────────
    console.print("\n[bold cyan]📝 Đang tạo báo cáo HTML...[/bold cyan]")
    audit_data = {
        'url':       url,
        'mode':      mode,
        'pages':     page_results,
        'timestamp': datetime.now()
    }

    output_dir = config.get('output_dir', 'reports')
    report_path = generate_report(audit_data, output_dir=os.path.join(os.path.dirname(__file__), output_dir))
    abs_path = os.path.abspath(report_path)

    console.print(f"\n[bold green]✅ Báo cáo đã lưu:[/bold green]")
    console.print(f"   [cyan]{abs_path}[/cyan]")

    # Auto open
    if config.get('auto_open_report', True):
        webbrowser.open(f'file://{abs_path}')
        console.print("[green]🌐 Báo cáo đã mở trên browser![/green]")
    else:
        open_now = Prompt.ask("\n[bold]Mở báo cáo trên browser ngay?[/bold]", choices=["y", "n"], default="y")
        if open_now == "y":
            webbrowser.open(f'file://{abs_path}')

    console.print(Panel(
        f"[bold green]🎉 Audit hoàn tất![/bold green]\n\n"
        f"  Trang đã quét: [bold]{len(pages)}[/bold]\n"
        f"  Lỗi Critical: [bold red]{sum(1 for i in all_issues if i['status']=='critical')}[/bold red]\n"
        f"  Cảnh báo: [bold yellow]{sum(1 for i in all_issues if i['status']=='warning')}[/bold yellow]\n"
        f"  Đã pass: [bold green]{sum(1 for i in all_issues if i['status']=='pass')}[/bold green]\n\n"
        f"  📄 Báo cáo: {os.path.basename(abs_path)}",
        border_style="green", title="Hoàn tất"
    ))


if __name__ == '__main__':
    main()
