@echo off
echo ========================================
echo Starting Flask Server
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python packages...
py -m pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing Flask...
    py -m pip install -r requirements.txt
)

echo.
echo ========================================
echo Starting Flask Server
echo ========================================
echo.
echo Server will start on: http://localhost:5000
echo (Database connection will be tested on startup)
echo.
echo Keep this window open!
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

py run.py

pause
