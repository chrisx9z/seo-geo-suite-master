import os
import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from seo_geo_suite.core.onpage import OnpageChecker
from seo_geo_suite.core.auditor import WebsiteAuditor
from seo_geo_suite.core.geo_writer import GeoWriter
from seo_geo_suite.core.css_fixer import CssFixer
from seo_geo_suite.core.asset_builder import AssetBuilder
from seo_geo_suite.core.keyword_planner import KeywordPlanner

import sys
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from modules.wp_ai_autopilot.autopilot_orchestrator import WpAiAutopilot
from modules.citability_engine import check_url as check_citability
from modules.prompt_injection_guard import check_url as check_prompt_injection
from modules.ai_crawler_access import check_access as check_ai_bot_access
from modules.sitemap_engine import check_sitemap as check_sitemap_deep
from modules.vps_cloudflare_aapanel.vps_automation import CloudflareManager

app = FastAPI(title="SEO & GEO Master Suite Dashboard")

static_dir = os.path.join(BASE_DIR, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

assets_dir = os.path.join(ROOT_DIR, "assets")
os.makedirs(assets_dir, exist_ok=True)
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

output_dir = os.path.join(ROOT_DIR, "output")
os.makedirs(output_dir, exist_ok=True)
app.mount("/output", StaticFiles(directory=output_dir), name="output")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

onpage_checker = OnpageChecker()
auditor = WebsiteAuditor()
geo_writer = GeoWriter()
css_fixer = CssFixer()
asset_builder = AssetBuilder()
keyword_planner = KeywordPlanner()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/onpage")
async def api_onpage(url: str = Form(...)):
    res = onpage_checker.analyze_url(url)
    return JSONResponse(content=res)

@app.post("/api/audit")
async def api_audit(url: str = Form(...)):
    res = auditor.audit_robots_and_sitemap(url)
    return JSONResponse(content=res)

@app.post("/api/write")
async def api_write(topic: str = Form(...), keyword: str = Form(...), author: str = Form("Chuyên gia SEO/GEO")):
    res = geo_writer.generate_article(topic=topic, target_keyword=keyword, author=author)
    return JSONResponse(content=res)

@app.post("/api/plan")
async def api_plan(seed: str = Form(...)):
    res = keyword_planner.generate_growth_roadmap(seed)
    return JSONResponse(content=res)

@app.post("/api/ui")
async def api_ui(type: str = Form(...), brand: str = Form("MyBrand")):
    if type == "menu":
        code = asset_builder.generate_menu_component(brand_name=brand)
    elif type == "footer":
        code = asset_builder.generate_footer_component(brand_name=brand)
    elif type == "breadcrumbs":
        code = asset_builder.generate_breadcrumbs([
            {"name": "Trang Chủ", "url": "/"},
            {"name": "Danh Mục", "url": "/danh-muc"},
            {"name": "Bài Viết Mẫu", "url": "/danh-muc/bai-viet"}
        ])
    else:
        code = ""
    return JSONResponse(content={"code": code, "type": type})

@app.post("/api/css")
async def api_css(css_code: str = Form(...)):
    res = css_fixer.check_css_string(css_code)
    return JSONResponse(content=res)

@app.get("/api/autopilot/sites")
async def api_autopilot_sites():
    """Returns list of configured sites for M-Auto-Pilot."""
    sites = []
    for c_rel in [os.path.join("private", "sites.local.json"), "config.json", os.path.join("config", "sites.json")]:
        c_path = os.path.abspath(os.path.join(ROOT_DIR, c_rel))
        if os.path.exists(c_path):
            try:
                with open(c_path, "r", encoding="utf-8") as f:
                    conf = json.load(f)
                    for s in conf.get("sites", []):
                        sites.append({
                            "site_id": s.get("site_id", ""),
                            "name": s.get("name", s.get("site_id", "")),
                            "url": s.get("url", ""),
                            "admin_user": s.get("admin_user", "admin")
                        })
                    if sites:
                        break
            except Exception:
                pass
    return JSONResponse(content={"sites": sites})

@app.post("/api/autopilot/publish")
async def api_autopilot_publish(
    site_id: str = Form(...),
    topic: str = Form(...),
    status: str = Form("publish"),
    category: int = Form(4),
    date: Optional[str] = Form(None),
    dry_run: bool = Form(False)
):
    """Executes M-Auto-Pilot pipeline for specified site."""
    wp_url = site_id if site_id.startswith("http") else f"https://{site_id}"
    admin_user = os.getenv("WP_ADMIN_USER", "admin")
    admin_pass = os.getenv("WP_ADMIN_PASSWORD", "")

    # Look up site credentials
    for c_rel in [os.path.join("private", "sites.local.json"), "config.json", os.path.join("config", "sites.json")]:
        c_path = os.path.abspath(os.path.join(ROOT_DIR, c_rel))
        if os.path.exists(c_path):
            try:
                with open(c_path, "r", encoding="utf-8") as f:
                    conf = json.load(f)
                    for s in conf.get("sites", []):
                        if site_id == s.get("site_id") or site_id in s.get("url", "") or site_id in s.get("name", "").lower():
                            wp_url = s.get("url", wp_url)
                            admin_user = s.get("admin_user", admin_user)
                            admin_pass = s.get("admin_pass") or s.get("admin_password") or admin_pass
                            break
            except Exception:
                pass
        if admin_pass:
            break

    try:
        autopilot = WpAiAutopilot(wp_url=wp_url, admin_user=admin_user, admin_pass=admin_pass)
        res = autopilot.produce_and_publish(
            topic=topic,
            category_ids=[category],
            status=status,
            schedule_date=date,
            dry_run=dry_run
        )
        # Convert absolute local asset paths to relative URLs for dashboard display
        if "banner_path" in res and res["banner_path"]:
            res["banner_url"] = f"/assets/banners/{os.path.basename(res['banner_path'])}"
        if "diagram_path" in res and res["diagram_path"]:
            res["diagram_url"] = f"/assets/banners/{os.path.basename(res['diagram_path'])}"
        if "link" in res and res["link"].startswith(ROOT_DIR):
            res["preview_url"] = f"/output/posts/{os.path.basename(res['link'])}"
        return JSONResponse(content=res)
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/citability")
async def api_citability(url: str = Form(...)):
    try:
        res = check_citability(url)
        return JSONResponse(content=res)
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/injection")
async def api_injection(url: str = Form(...)):
    try:
        res = check_prompt_injection(url)
        return JSONResponse(content=res)
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/ai-bots")
async def api_ai_bots(url: str = Form(...)):
    try:
        res = check_ai_bot_access(url)
        return JSONResponse(content=res)
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/sitemap-deep")
async def api_sitemap_deep(url: str = Form(...)):
    try:
        res = check_sitemap_deep(url)
        return JSONResponse(content=res)
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/devops/cf-purge")
async def api_cf_purge(domain: str = Form(...)):
    try:
        cf = CloudflareManager()
        ok = cf.purge_cache(domain)
        return JSONResponse(content={"status": "success" if ok else "failed", "domain": domain})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

