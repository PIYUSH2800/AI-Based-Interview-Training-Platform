@echo off
title AI Interview Platform - Frontend (Port 5173)
color 0B

echo ============================================================
echo   AI Interview Platform — Frontend Dev Server
echo ============================================================
echo.

cd /d "%~dp0frontend"

echo Checking npm and dependencies...
if not exist node_modules (
    echo [INFO] node_modules not found. Installing packages...
    call npm install
)

echo Starting Vite dev server on http://localhost:5173 ...
echo Press Ctrl+C to stop the server.
echo.

call npm run dev -- --host 127.0.0.1 --port 5173
pause
