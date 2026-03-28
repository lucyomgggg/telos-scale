#!/usr/bin/env bash

# Exit on first error
set -e

echo "=== Telos-Scale Setup ==="

# 1. Check if Docker is running (Required for Sandbox)
echo "Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Attempting to start Docker..."
    if [[ "$(uname)" == "Darwin" ]]; then
        open -a Docker
    elif [[ "$(expr substr $(uname -s) 1 5)" == "Linux" ]]; then
        sudo systemctl start docker || { echo "Please start Docker manually."; exit 1; }
    else
        echo "Please start Docker manually."
        exit 1
    fi
    
    echo "Waiting for Docker to be ready..."
    MAX_RETRIES=30
    RETRY_COUNT=0
    until docker info > /dev/null 2>&1 || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
        sleep 2
        ((RETRY_COUNT++))
        echo -n "."
    done
    echo ""
    
    if ! docker info > /dev/null 2>&1; then
        echo "Timeout: Docker failed to start. Please open Docker Desktop manually."
        exit 1
    fi
    echo "Docker is ready."
else
    echo "Docker is already running."
fi

# 2. Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists."
fi

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Install requirements and the package
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 5. Copy templates
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "NOTE: Please edit .env with your actual API key before running!"
fi

if [ ! -f "config.yml" ]; then
    echo "Creating config.yml from template..."
    cp config.example.yml config.yml
fi

echo "=== Setup Complete ==="
echo "To run the system, just execute: ./run.sh"
