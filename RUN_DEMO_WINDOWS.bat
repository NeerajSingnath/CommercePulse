@echo off
setlocal
cd /d "%~dp0"
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed. Use Python 3.11 or 3.12 and retry.
  pause
  exit /b 1
)
python scripts\quickstart.py --demo
if errorlevel 1 (pause & exit /b 1)
start "" "reports\interactive_dashboard.html"
python -m streamlit run app\dashboard.py
