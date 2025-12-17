# Massar - Start Frontend and Backend Servers
# This script starts both the backend (FastAPI) and frontend (React Router) servers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Massar - Starting Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory (project root)
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"

# Check if directories exist
if (-not (Test-Path $backendDir)) {
    Write-Host "Error: Backend directory not found at $backendDir" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $frontendDir)) {
    Write-Host "Error: Frontend directory not found at $frontendDir" -ForegroundColor Red
    exit 1
}

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    return $connection
}

# Check if ports are already in use
if (Test-Port -Port 8000) {
    Write-Host "Warning: Port 8000 (backend) is already in use!" -ForegroundColor Yellow
}

if (Test-Port -Port 5173) {
    Write-Host "Warning: Port 5173 (frontend) is already in use!" -ForegroundColor Yellow
}

Write-Host "Starting Backend Server (FastAPI) on port 8000..." -ForegroundColor Green
Write-Host "Starting Frontend Server (React Router) on port 5173..." -ForegroundColor Green
Write-Host ""

# Start Backend Server in a new window
$backendScript = @"
cd `"$backendDir`"
Write-Host 'Backend Server Starting...' -ForegroundColor Green
Write-Host 'Backend will be available at: http://localhost:8000' -ForegroundColor Cyan
Write-Host 'API Docs at: http://localhost:8000/docs' -ForegroundColor Cyan
Write-Host ''
uvicorn app.main:app --reload --port 8000
"@

$backendScriptPath = Join-Path $env:TEMP "massar-backend.ps1"
$backendScript | Out-File -FilePath $backendScriptPath -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$backendScriptPath'" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 2

# Start Frontend Server in a new window
$frontendScript = @"
cd `"$frontendDir`"
Write-Host 'Frontend Server Starting...' -ForegroundColor Green
Write-Host 'Frontend will be available at: http://localhost:5173' -ForegroundColor Cyan
Write-Host ''
npm run dev
"@

$frontendScriptPath = Join-Path $env:TEMP "massar-frontend.ps1"
$frontendScript | Out-File -FilePath $frontendScriptPath -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$frontendScriptPath'" -WindowStyle Normal

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Servers Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "Frontend:    http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "Two new PowerShell windows have been opened:" -ForegroundColor Cyan
Write-Host "  - One for the Backend server" -ForegroundColor White
Write-Host "  - One for the Frontend server" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop the respective server." -ForegroundColor Gray
Write-Host ""

