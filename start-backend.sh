#!/bin/bash
cd ~/automation-suite/backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
python3.11 -m pip install --upgrade pip
pip3.11 install -r requirements.txt

# Start the FastAPI application
python3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8000