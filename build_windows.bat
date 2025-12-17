@echo off
REM Build Bongo Cat for Windows

echo ================================================
echo Bongo Cat Windows Build Script
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher from https://www.python.org
    pause
    exit /b 1
)

REM Run build script
python build.py

echo.
echo Build complete! Check the dist folder.
pause
