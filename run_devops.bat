@echo off
chcp 65001 > nul
call .\venv\Scripts\python.exe cli\master_devops.py %*
