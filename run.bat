@echo off
setlocal enabledelayedexpansion
:: run.bat

if not exist ".venv" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

:: Check if Docker is running
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
        echo Timeout waiting for Docker to start. Please check Docker Desktop.
        pause
        exit /b 1
    )
    goto :wait_loop
)

:docker_ready
call .venv\Scripts\activate
echo Starting Telos-Scale using settings from config.yml...
telos-scale run
pause
