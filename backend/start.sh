#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Install dependencies if requirements.txt is newer than the last install
if [ requirements.txt -nt venv/pyvenv.cfg ]; then
    echo "Installing/updating dependencies..."
    pip3 install -r requirements.txt
fi

# Run the application
echo "Starting POS System API..."
python3 run.py
