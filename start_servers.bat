@echo off
echo ========================================
echo   MaiChart Music Import Assistant
echo ========================================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo Starting servers...
echo.

echo [1/2] Starting backend server (FastAPI on port 8000)...
start "MaiChart Backend" cmd /c "uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo [2/2] Starting frontend server (HTTP server on port 3000)...
start "MaiChart Frontend" cmd /c "python -m http.server 3000"

echo.
echo Waiting for servers to start...
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo Servers started successfully!
echo.
echo Backend API:  http://127.0.0.1:8000
echo Frontend App: http://127.0.0.1:3000
echo.
echo Opening frontend in browser...
start http://127.0.0.1:3000
echo.
echo Press any key to stop all servers and exit...
pause > nul

echo.
echo Stopping servers...
taskkill /f /im python.exe > nul 2>&1
taskkill /f /im uvicorn.exe > nul 2>&1
echo All servers stopped.
echo.
echo Goodbye!