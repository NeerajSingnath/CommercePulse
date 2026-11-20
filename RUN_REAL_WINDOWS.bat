@echo off
setlocal
cd /d "%~dp0"
python -m pip install -r requirements.txt kagglehub
if errorlevel 1 (pause & exit /b 1)
python scripts\download_olist.py
if errorlevel 1 (pause & exit /b 1)
python scripts\quickstart.py
if errorlevel 1 (pause & exit /b 1)
start "" "reports\interactive_dashboard.html"
python -m streamlit run app\dashboard.py
