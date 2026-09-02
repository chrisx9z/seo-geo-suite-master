import sys
import os
import argparse
import json

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from seo_geo_suite.core.onpage import OnpageChecker
from seo_geo_suite.core.auditor import WebsiteAuditor
from seo_geo_suite.core.geo_writer import GeoWriter
from seo_geo_suite.core.css_fixer import CssFixer
from seo_geo_suite.core.asset_builder import AssetBuilder
from seo_geo_suite.core.keyword_planner import KeywordPlanner

console = Console(force_terminal=True, legacy_windows=False)

def show_banner():
    banner = """
  =============================================================
  ⚡  SEO & GEO (GENERATIVE ENGINE OPTIMIZATION) MASTER SUITE  ⚡
  =============================================================
    """
    console.print(f"[bold cyan]{banner}[/bold cyan]")

def run_onpage(url: str):
    console.print(f"[bold green]🔍 Đang phân tích Onpage & Schema cho:[/] [yellow]{url}[/]")
    checker = OnpageChecker()
    result = checker.analyze_url(url)

    if result.get("status") == "error":
        console.print(f"[bold red]❌ Lỗi khi tải URL:[/] {result.get('error')}")
        return

    table = Table(title=f"Báo Cáo Onpage: {url}", show_header=True, header_style="bold magenta")
    table.add_column("Chỉ số", style="cyan", width=25)
    table.add_column("Giá trị / Trạng thái", style="white")

    table.add_row("Điểm SEO On-page", f"[bold green]{result['seo_score']}/100[/]")
    table.add_row("Điểm GEO AI Citability", f"[bold yellow]{result['geo_citability_score']}/100[/]")
    table.add_row("Title", f"{result['title']['text']} ({result['title']['length']} ký tự)")
    table.add_row("Meta Description", f"{result['meta_description']['text']} ({result['meta_description']['length']} ký tự)")
    table.add_row("Thẻ H1", f"{len(result['headings'].get('h1', []))} thẻ (Trạng thái: {result['h1_status']})")
    table.add_row("Canonical", result['canonical'] or "[red]Chưa có[/]")
    table.add_row("Hình ảnh thiếu Alt", f"{result['images']['missing_alt_count']} / {result['images']['total']}")
    table.add_row("Schemas Tìm thấy", ", ".join(result['geo_signals']['schema_types_found']) or "[red]Chưa có[/]")
    table.add_row("Tín hiệu E-E-A-T / Entity", "[green]Đầy đủ[/]" if result['geo_signals']['has_author_or_entity'] else "[yellow]Cần bổ sung[/]")

    console.print(table)

    if result["issues"]:
        console.print("\n[bold red]⚠️ Các vấn đề phát hiện được:[/]")
        for iss in result["issues"]:
            console.print(f"  • [red]{iss}[/]")

    if result["recommendations"]:
        console.print("\n[bold green]💡 Khuyến nghị tối ưu:[/]")
        for rec in result["recommendations"]:
            console.print(f"  • [green]{rec}[/]")

def run_geo_write(topic: str, keyword: str):
    console.print(f"[bold blue]✍️ Đang tạo bài viết GEO/SEO cho chủ đề:[/] [yellow]{topic}[/]")
    writer = GeoWriter()
    article = writer.generate_article(topic=topic, target_keyword=keyword)

    os.makedirs("reports/articles", exist_ok=True)
    filename = f"reports/articles/{article['topic'].lower().replace(' ', '_')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(article["content_markdown"])
        f.write("\n\n## 📄 Cấu Trúc JSON-LD Schema\n`json\n")
        f.write(article["article_schema_json"])
        f.write("\n`\n")
        f.write("\n## ❓ FAQPage Schema\n`json\n")
        f.write(article["faq_schema_json"])
        f.write("\n`\n")

    console.print(Panel(f"[bold green]✅ Bài viết đã được tạo thành công![/]\n\n"
                        f"[bold]Tiêu đề:[/] {article['title']}\n"
                        f"[bold]Meta Desc:[/] {article['meta_description']}\n"
                        f"[bold]Đã lưu vào:[/] [cyan]{filename}[/]\n"
                        f"[bold]Entry llms.txt:[/] {article['llms_entry']}",
                        title="Kết Quả Tạo Nội Dung GEO/SEO", expand=False))

def run_keyword_plan(seed: str):
    console.print(f"[bold magenta]📈 Đang phân tích từ khóa & lập kế hoạch cho:[/] [yellow]{seed}[/]")
    planner = KeywordPlanner()
    plan = planner.generate_growth_roadmap(seed)

    table = Table(title=f"Kế Hoạch Từ Khóa & Topic Clusters: '{seed}'", show_header=True)
    table.add_column("Cụm chủ đề / Pillar Page", style="cyan")
    table.add_column("Số từ khóa", style="yellow", justify="right")
    table.add_column("Từ khóa chính trong cụm", style="white")

    for cl in plan["clusters"]:
        table.add_row(cl["pillar_page"], str(cl["cluster_size"]), ", ".join(cl["keywords"][:4]))

    console.print(table)

    roadmap_table = Table(title="Lộ Trình Triển Khai 30 Ngày", show_header=True)
    roadmap_table.add_column("Giai đoạn / Tuần", style="green")
    roadmap_table.add_column("Mục tiêu triển khai", style="white")

    for w in plan["roadmap_30_days"]:
        roadmap_table.add_row(w["phase"], w["deliverables"])

    console.print(roadmap_table)

    # Save to file
    os.makedirs("reports", exist_ok=True)
    plan_file = f"reports/roadmap_{seed.replace(' ', '_')}.json"
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    console.print(f"[bold green]💾 Đã lưu toàn bộ kế hoạch vào:[/] [cyan]{plan_file}[/]")

def run_ui_asset(asset_type: str, brand: str = "MyBrand"):
    builder = AssetBuilder()
    os.makedirs("reports/components", exist_ok=True)
    
    if asset_type in ["menu", "header", "navbar"]:
        code = builder.generate_menu_component(brand_name=brand)
        filepath = "reports/components/header_menu.html"
    elif asset_type in ["footer"]:
        code = builder.generate_footer_component(brand_name=brand)
        filepath = "reports/components/footer.html"
    elif asset_type in ["breadcrumbs", "breadcrumb"]:
        code = builder.generate_breadcrumbs([
            {"name": "Trang Chủ", "url": "/"},
            {"name": "Chuyên Mục", "url": "/danh-muc"},
            {"name": "Bài Viết Hiện Tại", "url": "/danh-muc/bai-viet"}
        ])
        filepath = "reports/components/breadcrumbs.html"
    else:
        console.print("[red]Loại UI không hợp lệ. Hãy chọn: menu, footer, breadcrumbs[/]")
        return

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)

    console.print(Panel(f"[bold green]✅ Đã tạo thành công component:[/] [yellow]{asset_type.upper()}[/]\n[bold]Lưu tại:[/] [cyan]{filepath}[/]\n\nCode hỗ trợ sẵn Responsive, Tailwind CSS & Schema.org JSON-LD.", title="Web Asset Component"))

def run_css_audit(filepath: str):
    console.print(f"[bold pink]🛠️ Đang kiểm tra CSS file:[/] [yellow]{filepath}[/]")
    if not os.path.exists(filepath):
        console.print(f"[bold red]❌ File {filepath} không tồn tại.[/]")
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    fixer = CssFixer()
    res = fixer.check_css_string(content)
    
    table = Table(title=f"Kết Quả Kiểm Tra CSS: {filepath}", show_header=True)
    table.add_column("Chỉ số", style="cyan")
    table.add_column("Kết quả", style="white")
    table.add_row("Số rules CSS ước tính", str(res["total_rules_estimate"]))
    table.add_row("Lạm dụng !important", str(res["important_count"]))
    console.print(table)

    if res["issues"]:
        console.print("\n[bold red]⚠️ Lỗi phát hiện được:[/]")
        for iss in res["issues"]:
            console.print(f"  • [red]{iss}[/]")
    if res["recommendations"]:
        console.print("\n[bold green]💡 Khuyến nghị tối ưu:[/]")
        for rec in res["recommendations"]:
            console.print(f"  • [green]{rec}[/]")

def main():
    show_banner()
    parser = argparse.ArgumentParser(description="SEO & GEO Master Suite CLI")
    subparsers = parser.add_subparsers(dest="command")

    # 1. Onpage
    onpage_parser = subparsers.add_parser("onpage", help="Kiểm tra Onpage SEO & GEO Citability")
    onpage_parser.add_argument("url", nargs="?", default=None, help="URL cần kiểm tra")
    onpage_parser.add_argument("--url", "-u", dest="url_opt", help="URL cần kiểm tra (dạng cờ)")

    # 2. Audit
    audit_parser = subparsers.add_parser("audit", help="Audit toàn diện website & robots.txt / sitemap / link hỏng")
    audit_parser.add_argument("url", nargs="?", default=None, help="Domain hoặc URL website")
    audit_parser.add_argument("--url", "-u", dest="url_opt", help="Domain hoặc URL website (dạng cờ)")

    # 3. Write
    write_parser = subparsers.add_parser("write", help="Viết bài chuẩn SEO/GEO")
    write_parser.add_argument("--topic", required=True, help="Chủ đề bài viết")
    write_parser.add_argument("--keyword", required=True, help="Từ khóa chính")

    # 4. Keyword Planner
    plan_parser = subparsers.add_parser("plan", help="Nghiên cứu từ khóa & lập lộ trình phát triển")
    plan_parser.add_argument("--seed", required=True, help="Từ khóa gốc")

    # 5. UI Assets
    ui_parser = subparsers.add_parser("ui", help="Tạo Header, Menu, Footer hoặc Breadcrumbs")
    ui_parser.add_argument("--type", required=True, choices=["menu", "footer", "breadcrumbs"], help="Loại component")
    ui_parser.add_argument("--brand", default="MyBrand", help="Tên thương hiệu")

    # 6. CSS
    css_parser = subparsers.add_parser("css", help="Kiểm tra và chuẩn đoán lỗi CSS")
    css_parser.add_argument("file", nargs="?", default=None, help="Đường dẫn file CSS")
    css_parser.add_argument("--file", "-f", dest="file_opt", help="Đường dẫn file CSS (dạng cờ)")

    # 7. Dashboard
    subparsers.add_parser("dashboard", help="Khởi chạy Web Dashboard giao diện trực quan")

    args = parser.parse_args()

    if args.command == "onpage":
        target_url = args.url or args.url_opt
        if not target_url:
            console.print("[bold red]❌ Vui lòng cung cấp URL cần kiểm tra.[/]")
            return
        run_onpage(target_url)
    elif args.command == "audit":
        target_url = args.url or args.url_opt
        if not target_url:
            console.print("[bold red]❌ Vui lòng cung cấp Domain hoặc URL website cần audit.[/]")
            return
        console.print(f"[bold green]🔍 Đang chạy Audit cho:[/] [yellow]{target_url}[/]")
        auditor = WebsiteAuditor()
        data = auditor.audit_robots_and_sitemap(target_url)
        console.print(f"Robots.txt: {'[green]Tìm thấy[/]' if data['robots']['found'] else '[red]Thiếu[/]'}")
        console.print(f"Sitemap.xml: {'[green]Tìm thấy ' + str(data['sitemap']['urls_count']) + ' URLs[/]' if data['sitemap']['found'] else '[red]Thiếu[/]'}")
        console.print(f"llms.txt (AI Crawlers): {'[green]Đã cấu hình[/]' if data['llms_txt']['found'] else '[yellow]Chưa có (Nên bổ sung)[/]'}")
    elif args.command == "write":
        run_geo_write(args.topic, args.keyword)
    elif args.command == "plan":
        run_keyword_plan(args.seed)
    elif args.command == "ui":
        run_ui_asset(args.type, args.brand)
    elif args.command == "css":
        target_file = args.file or args.file_opt
        if not target_file:
            console.print("[bold red]❌ Vui lòng cung cấp đường dẫn file CSS.[/]")
            return
        run_css_audit(target_file)
    elif args.command == "dashboard":
        console.print("[bold green]🚀 Đang khởi động Web Dashboard tại http://localhost:8000 ...[/]")
        os.system(f"{sys.executable} -m uvicorn seo_geo_suite.dashboard.app:app --host 0.0.0.0 --port 8000 --reload")
    else:
        # Interactive mode
        console.print("[bold yellow]Chọn một tính năng để thực hiện:[/]")
        console.print("  1. Kiểm tra On-page SEO & Schema (Onpage Checker)")
        console.print("  2. Audit Website & Kiểm tra Robots / Sitemap / AI Bots")
        console.print("  3. Viết bài viết mới chuẩn GEO / SEO (AI Article Writer)")
        console.print("  4. Lên kế hoạch từ khóa & Lộ trình phát triển 30 ngày")
        console.print("  5. Tạo Menu / Footer / Breadcrumbs chuẩn SEO UI")
        console.print("  6. Kiểm tra và sửa lỗi CSS (CSS Fixer)")
        console.print("  7. Khởi chạy Web Dashboard trực quan")
        
        choice = Prompt.ask("Nhập lựa chọn (1-7)", choices=["1", "2", "3", "4", "5", "6", "7"])
        if choice == "1":
            url = Prompt.ask("Nhập URL cần kiểm tra")
            run_onpage(url)
        elif choice == "2":
            url = Prompt.ask("Nhập domain website cần audit")
            auditor = WebsiteAuditor()
            data = auditor.audit_robots_and_sitemap(url)
            console.print(data)
        elif choice == "3":
            topic = Prompt.ask("Nhập chủ đề bài viết")
            keyword = Prompt.ask("Nhập từ khóa chính")
            run_geo_write(topic, keyword)
        elif choice == "4":
            seed = Prompt.ask("Nhập từ khóa gốc")
            run_keyword_plan(seed)
        elif choice == "5":
            t = Prompt.ask("Chọn loại component", choices=["menu", "footer", "breadcrumbs"])
            b = Prompt.ask("Tên thương hiệu", default="MyBrand")
            run_ui_asset(t, b)
        elif choice == "6":
            f_path = Prompt.ask("Nhập đường dẫn file CSS")
            run_css_audit(f_path)
        elif choice == "7":
            console.print("[bold green]🚀 Đang khởi động Web Dashboard tại http://localhost:8000 ...[/]")
            os.system(f"{sys.executable} -m uvicorn seo_geo_suite.dashboard.app:app --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main()

