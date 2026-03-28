@echo off
:: run.bat

if not exist ".venv" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate
echo Starting Telos-Scale using settings from config.yml...
telos-scale run
pause
