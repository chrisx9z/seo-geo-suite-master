@echo off
chcp 65001 > nul
set PYTHONUTF8=1
call .\venv\Scripts\python.exe -m seo_geo_suite %*
