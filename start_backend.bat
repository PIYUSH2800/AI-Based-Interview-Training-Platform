@echo off
title AI Interview Platform - Backend API (Port 8000)
color 0A

echo ============================================================
echo   AI Interview Platform — Backend Server
echo ============================================================
echo.

cd /d "%~dp0backend"

echo Checking Python environment...
python -c "import fastapi, uvicorn; print('FastAPI & Uvicorn verified.')"
if %errorlevel% neq 0 (
    echo [ERROR] Python dependencies missing!
    echo Run: pip install -r requirements.txt
    pause
    exit /b %errorlevel%
)

echo Starting Uvicorn server on http://localhost:8000 ...
echo Press Ctrl+C to stop the server.
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
