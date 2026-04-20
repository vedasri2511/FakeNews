@echo off
REM Start all services for Fake News Detection System

echo.
echo ================================================
echo   FAKE NEWS DETECTION SYSTEM - Starting
echo ================================================
echo.
echo timeout /t 2

REM Start Backend
echo [1/4] Starting Express Backend on port 5000...
start "Backend" cmd /k "cd c:\kafka\kafka-projects\NEWS\backend && npm start"
timeout /t 3

REM Start Frontend
echo [2/4] Starting React Frontend on port 3000...
start "Frontend" cmd /k "cd c:\kafka\kafka-projects\NEWS\frontend && npm start"
timeout /t 3

REM Start Kafka Producer
echo [3/4] Starting Kafka Producer...
start "Kafka Producer" cmd /k "cd c:\kafka\kafka-projects\NEWS && . .\.venv\Scripts\Activate.ps1; python kafka\producer.py"
timeout /t 2

REM Start Spark Consumer (Improved!)
echo [4/4] Starting Spark Streaming Consumer...
start "Spark Consumer" cmd /k "cd c:\kafka\kafka-projects\NEWS && . .\.venv\Scripts\Activate.ps1; python spark\spark_stream.py"
timeout /t 2

echo.
echo ================================================
echo   ✓ All services started!
echo ================================================
echo.
echo Services running:
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:3000
echo.
echo Kafka Producer is fetching articles...
echo Spark Streaming is processing articles...
echo.
pause
