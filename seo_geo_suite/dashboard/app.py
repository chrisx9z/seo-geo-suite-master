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

app = FastAPI(title="SEO & GEO Master Suite Dashboard")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

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
