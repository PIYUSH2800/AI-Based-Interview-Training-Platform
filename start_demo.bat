@echo off
title AI Interview Platform — Localhost College Demonstration
color 0F

echo ============================================================
echo   AI INTERVIEW TRAINING PLATFORM — LOCALHOST DEMO LAUNCHER
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/4] Running pre-flight environment check...
python verify_environment.py
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Some environment checks reported warnings or errors.
    echo Press any key to attempt launching anyway, or Ctrl+C to abort.
    pause >nul
)

echo.
echo [2/4] Starting Backend Server (FastAPI + SQLite) on port 8000...
start "AI Interview Platform — Backend (Port 8000)" cmd /c "%~dp0start_backend.bat"

echo.
echo [3/4] Starting Frontend Dev Server (React + Vite) on port 5173...
start "AI Interview Platform — Frontend (Port 5173)" cmd /c "%~dp0start_frontend.bat"

echo.
echo [4/4] Waiting 4 seconds for servers to initialize...
timeout /t 4 >nul

echo.
echo Launching web browser to http://localhost:5173 ...
start http://localhost:5173

echo.
echo ============================================================
echo   DEMONSTRATION SYSTEM IS ACTIVE!
echo ============================================================
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000 (Docs: http://localhost:8000/docs)
echo ============================================================
echo.
echo To stop all running servers, press 'S' and hit Enter.
echo To exit this menu, press Enter.
echo.
set /p user_action="Selection [S=Stop Servers, Enter=Exit]: "

if /i "%user_action%"=="S" (
    call "%~dp0stop_servers.bat"
)

exit /b 0
