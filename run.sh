#!/usr/bin/env bash
# run.sh

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Attempting to start Docker..."
    if [[ "$(uname)" == "Darwin" ]]; then
        open -a Docker
    elif [[ "$(expr substr $(uname -s) 1 5)" == "Linux" ]]; then
        systemctl start docker || { echo "Please start Docker manually."; exit 1; }
    else
        echo "Please start Docker manually."
        exit 1
    fi
    
    echo "Waiting for Docker to start..."
    for i in {1..30}; do
        if docker info > /dev/null 2>&1; then
            echo "Docker started successfully."
            break
        fi
        sleep 2
    done
    
    if ! docker info > /dev/null 2>&1; then
        echo "Timeout waiting for Docker to start. Please check Docker Desktop."
        exit 1
    fi
fi

source .venv/bin/activate

echo "Starting Telos-Scale using settings from config.yml..."
telos-scale run
