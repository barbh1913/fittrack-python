@echo off
cd /d "%~dp0"
cd "frontend\static"
echo Starting React development server...
echo Make sure Flask is running on port 5000!
echo.
call npm run dev
