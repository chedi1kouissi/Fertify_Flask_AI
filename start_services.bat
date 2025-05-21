@echo off
echo ======================================================
echo        Starting Fertify GreenAI Services
echo ======================================================

echo Checking for existing processes on ports 5001 and 5002...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5001 ^| findstr LISTENING') do (
    echo Found process using port 5001: %%a
    taskkill /F /PID %%a 2>nul
    echo Killed process %%a
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5002 ^| findstr LISTENING') do (
    echo Found process using port 5002: %%a
    taskkill /F /PID %%a 2>nul
    echo Killed process %%a
)

echo Starting services...
python controller.py

echo Press any key to exit...
pause 