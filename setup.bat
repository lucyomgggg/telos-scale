@echo off
setlocal enabledelayedexpansion
echo === Telos-Scale Setup ===

:: 1. Check if Docker is running
docker info >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Docker is not running. Attempting to start Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Waiting for Docker to start...
    set "MAX_TRIES=30"
    set "TRIES=0"
    :wait_loop
    timeout /t 2 /nobreak >nul
    docker info >nul 2>nul
    if !ERRORLEVEL! equ 0 (
        echo Docker started successfully.
        goto :docker_ready
    )
    set /a TRIES+=1
    if !TRIES! geq !MAX_TRIES! (
        echo Timeout waiting for Docker to start. Please open Docker Desktop manually.
        pause
        exit /b 1
    )
    goto :wait_loop
) else (
    echo Docker is already running.
)

:docker_ready
:: 2. Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating Python virtual environment ^(.venv^)...
    python -m venv .venv
) else (
    echo Virtual environment already exists.
)

:: 3. Activate virtual environment
call .venv\Scripts\activate

:: 4. Install requirements
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

:: 5. Copy templates
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo NOTE: Please edit .env with your actual API key before running!
)

if not exist "config.yml" (
    echo Creating config.yml from template...
    copy config.example.yml config.yml
)

echo === Setup Complete ===
echo To run the system, just execute: run.bat
pause
