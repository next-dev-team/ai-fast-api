#!/bin/bash
set -e

# This script starts the development server.
# It activates the virtual environment and runs the main application.

VENV_ACTIVATION_PATHS=(
    ".venv/bin/activate"
    ".venv/Scripts/activate"
)

VENV_FOUND=false
for path in "${VENV_ACTIVATION_PATHS[@]}"; do
    if [ -f "$path" ]; then
        echo "Activating virtual environment from $path..."
        source "$path"
        VENV_FOUND=true
        break
    fi
done

if [ "$VENV_FOUND" = false ]; then
    echo "Virtual environment not found. Please run setup.sh to create it."
    exit 1
fi

# Run the main application
echo "Starting the development server..."
python main.py