@echo off
echo Starting Personal Task Planner Bot...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8 or later
    pause
    exit /b
)

REM Check if required packages are installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
)

REM Start the Flask API server
echo Starting Flask API server...
start "Flask API" python api.py

REM Give the server a moment to start
timeout /t 3 /nobreak >nul

REM Open the application in the default browser
echo Opening application in browser...
start "" "http://localhost:5000"

echo Application started successfully!
echo API server running on http://localhost:5000
echo Press any key to close this window...
pause >nul