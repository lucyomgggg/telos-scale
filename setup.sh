#!/usr/bin/env bash

# Exit on first error
set -e

echo "=== Telos-Scale Setup ==="

# 1. Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists."
fi

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Install requirements and the package
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -e .

# 4. Copy templates
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
