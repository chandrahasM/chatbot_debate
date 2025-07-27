@echo off
setlocal

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="install" goto install
if "%1"=="test" goto test
if "%1"=="run" goto run
if "%1"=="down" goto down
if "%1"=="clean" goto clean
if "%1"=="dev" goto dev

echo Unknown command: %1
goto help

:help
echo Available commands:
echo   run.bat install  - Install dependencies
echo   run.bat test     - Run tests
echo   run.bat run      - Run the service with Docker
echo   run.bat down     - Stop all services
echo   run.bat clean    - Remove all containers and images
echo   run.bat dev      - Run locally for development
goto end

:install
echo Checking required tools...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python3 is required. Install it from https://www.python.org/downloads/
    exit /b 1
)

docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is required. Install it from https://docs.docker.com/get-docker/
    exit /b 1
)

docker compose version >nul 2>&1
if errorlevel 1 (
    echo Docker Compose is required. Install it from https://docs.docker.com/compose/install/
    exit /b 1
)

echo Installing Python requirements...
pip install -r requirements.txt
echo Installation complete!
goto end

:test
echo Running tests...
pytest tests/
echo Tests completed!
goto end

:run
echo Starting the debate chatbot service...
docker compose up --build
echo Service started!
goto end

:down
echo Stopping services...
docker compose down
echo Services stopped.
goto end

:clean
echo Cleaning up containers and images...
docker compose down -v --rmi all
if exist chat.db del chat.db
echo Cleanup complete!
goto end

:dev
echo Starting development server...
echo API will be available at: http://localhost:8000
echo Press Ctrl+C to stop
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
goto end

:end
