@echo off
REM Massar - Start Frontend and Backend Servers
REM This script starts both the backend (FastAPI) and frontend (React Router) servers

echo ========================================
echo   Massar - Starting Servers
echo ========================================
echo.

REM Get the script directory (project root)
set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"

REM Check if directories exist
if not exist "%BACKEND_DIR%" (
    echo Error: Backend directory not found at %BACKEND_DIR%
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo Error: Frontend directory not found at %FRONTEND_DIR%
    pause
    exit /b 1
)

echo Starting Backend Server (FastAPI) on port 8000...
echo Starting Frontend Server (React Router) on port 5173...
echo.

REM Start Backend Server in a new window
start "Massar Backend Server" cmd /k "cd /d "%BACKEND_DIR%" && echo Backend Server Starting... && echo Backend will be available at: http://localhost:8000 && echo API Docs at: http://localhost:8000/docs && echo. && uvicorn app.main:app --reload --port 8000"

REM Wait a moment for backend to start
timeout /t 2 /nobreak >nul

REM Start Frontend Server in a new window
start "Massar Frontend Server" cmd /k "cd /d "%FRONTEND_DIR%" && echo Frontend Server Starting... && echo Frontend will be available at: http://localhost:5173 && echo. && npm run dev"

echo ========================================
echo   Servers Started!
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Frontend:    http://localhost:5173
echo.
echo Two new command windows have been opened:
echo   - One for the Backend server
echo   - One for the Frontend server
echo.
echo Close the windows or press Ctrl+C to stop the servers.
echo.
pause




