@echo off
setlocal
cd /d "%~dp0"
echo ======================================
echo  Mini E-commerce REST API - Quick Start
echo ======================================
where py >nul 2>nul
if not errorlevel 1 (
    set "PY_CMD=py"
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo ERROR: Python is not installed or not in PATH.
        echo Install Python 3.10+ from python.org and check Add to PATH.
        pause
        exit /b 1
    )
    set "PY_CMD=python"
)
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PY_CMD% -m venv .venv
    if errorlevel 1 goto :error
)
echo Installing packages (internet is required on the first run)...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :error
echo Applying database migrations...
.venv\Scripts\python.exe manage.py migrate
if errorlevel 1 goto :error
echo Loading sample products...
.venv\Scripts\python.exe manage.py seed_demo
if errorlevel 1 goto :error
echo.
echo API: http://127.0.0.1:8000/api/
echo Admin: http://127.0.0.1:8000/admin/
echo Press Ctrl+C to stop the server.
echo.
.venv\Scripts\python.exe manage.py runserver
pause
exit /b 0
:error
echo.
echo Setup failed. Check the error message above.
pause
exit /b 1
