@echo off
chcp 65001 > nul
call .\venv\Scripts\python.exe -m seo_geo_suite %*
