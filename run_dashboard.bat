@echo off
chcp 65001 > nul
echo =======================================================
echo Dang khoi dong SEO & GEO Master Suite Dashboard...
echo Truy cap tai: http://localhost:8000
echo =======================================================
call .\venv\Scripts\python.exe -m uvicorn seo_geo_suite.dashboard.app:app --host 127.0.0.1 --port 8000
