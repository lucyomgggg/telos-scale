@echo off
echo === Telos-Scale Setup ===

:: 1. Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating Python virtual environment ^(.venv^)...
    python -m venv .venv
) else (
    echo Virtual environment already exists.
)

:: 2. Activate virtual environment
call .venv\Scripts\activate

:: 3. Install requirements
echo Installing dependencies...
pip install -r requirements.txt
pip install -e .

:: 4. Copy templates
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
echo To run the system, just double-click: run.bat
pause
