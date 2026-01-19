@echo off
echo ========================================
echo Running Database Seed Script
echo ========================================
echo.

cd /d "%~dp0"

echo Starting seed script...
echo (This will test the database connection automatically)
echo.
py seed.py

if errorlevel 1 (
    echo.
    echo ❌ Seed script failed!
    echo Check the error messages above.
    echo.
) else (
    echo.
    echo ✅ Seed script completed successfully!
    echo.
)

pause
