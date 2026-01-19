@echo off
echo ========================================
echo Installing Python Requirements
echo ========================================
echo.

cd /d "%~dp0"

echo Installing packages from requirements.txt...
py -m pip install -r requirements.txt

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Next step: Run start-flask.bat to start the server
pause
