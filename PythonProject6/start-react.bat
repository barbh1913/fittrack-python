@echo off
cd /d "%~dp0"
cd "frontend\static"
echo Installing dependencies...
call npm install
echo Building React app...
call npm run build
echo.
echo React app built successfully!
echo Now run: python run.py
pause
