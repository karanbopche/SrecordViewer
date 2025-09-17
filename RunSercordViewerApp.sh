#!/bin/bash

PYTHON_COMMAND="python3"
if ! command -v "$PYTHON_COMMAND" &> /dev/null; then
    PYTHON_COMMAND="python"
    if ! command -v "$PYTHON_COMMAND" &> /dev/null; then
        echo "Error: Neither python3 nor python found."
        exit 1
    fi
fi

if [ ! -d "venv" ]; then
    echo creating virtual environment
    "$PYTHON_COMMAND" -m venv venv
fi

echo installing dependencies
source  venv/bin/activate
"$PYTHON_COMMAND" -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo pip failed to install required dependencies
    deactivate
    rm -rf venv
else
    "$PYTHON_COMMAND" main.py "$@"
    deactivate
fi
