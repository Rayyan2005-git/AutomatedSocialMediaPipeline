@echo off
echo =========================================
echo  Automated Social Media Pipeline Runner
echo =========================================
echo.

cd /d "%~dp0"

echo Running Phase 1: Selecting and Downloading Images...
call .\venv\Scripts\python.exe src\cli.py
if %errorlevel% neq 0 (
    echo [ERROR] Phase 1 failed!
    exit /b %errorlevel%
)

echo.
echo Running Phase 2: Photoroom Generation and Gemini Captions...
call .\venv\Scripts\python.exe src\phase2_cli.py
if %errorlevel% neq 0 (
    echo [ERROR] Phase 2 failed!
    exit /b %errorlevel%
)

echo.
echo Running Phase 3: Uploading to Instagram...
call .\venv\Scripts\python.exe src\phase3_cli.py --live
if %errorlevel% neq 0 (
    echo [ERROR] Phase 3 failed!
    exit /b %errorlevel%
)

echo.
echo =========================================
echo  Pipeline Complete!
echo =========================================
exit /b 0
