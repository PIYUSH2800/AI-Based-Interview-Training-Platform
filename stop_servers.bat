@echo off
title Stop AI Interview Platform Servers
color 0C

echo ============================================================
echo   Stopping Local AI Interview Platform Servers
echo ============================================================
echo.

echo Freeing port 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Terminating PID %%a on port 8000...
    taskkill /F /PID %%a >nul 2>&1
)

echo Freeing port 5173 (Frontend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo Terminating PID %%a on port 5173...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo [OK] All local servers stopped and ports freed.
timeout /t 3 >nul
exit /b 0
