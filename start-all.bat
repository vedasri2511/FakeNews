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

REM Start ML Prediction Service (CRITICAL!)
echo [3/4] Starting ML Prediction Service on port 5001...
start "ML Service" cmd /k "c:\kafka\kafka-projects\NEWS\.venv\Scripts\python.exe c:\kafka\kafka-projects\NEWS\ml\ml_service_enhanced.py"
timeout /t 2

REM NOTE: Kafka and Spark require separate Kafka broker setup
REM To enable streaming: Install Kafka and uncomment the lines below
REM
REM Start Kafka Producer
REM echo [4/5] Starting Kafka Producer...
REM start "Kafka Producer" cmd /k "cd c:\kafka\kafka-projects\NEWS && . .\.venv\Scripts\Activate.ps1; python kafka\producer.py"
REM timeout /t 2
REM
REM Start Spark Streaming Consumer
REM echo [5/5] Starting Spark Streaming Consumer...
REM start "Spark Consumer" cmd /k "cd c:\kafka\kafka-projects\NEWS && . .\.venv\Scripts\Activate.ps1; python spark\spark_stream.py"
REM timeout /t 2

echo.
echo ================================================
echo   ✓ Core services started!
echo ================================================
echo.
echo Services running:
echo   Backend:  http://localhost:5000
echo   ML Model: http://localhost:5001
echo   Frontend: http://localhost:3000
echo.
echo NOTE: Kafka/Spark streaming disabled (requires Kafka broker)
echo To enable: Install Kafka and uncomment streaming sections
echo.
pause
