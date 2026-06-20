@echo off
REM Production startup script for Wynreach Backend (Windows)

echo.
echo ========================================
echo  Wynreach Backend - Production Startup
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Copy .env.example to .env and fill in your production values
    pause
    exit /b 1
)

echo Validating environment...

REM Start Uvicorn with production settings
echo Starting Uvicorn server...
echo.

REM Option 1: Using Uvicorn directly
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

REM Option 2: Using Gunicorn (uncomment if gunicorn is installed)
REM gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 -k uvicorn.workers.UvicornWorker app.main:app

pause
