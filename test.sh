#!/bin/bash
set -e

# This script runs the test suite.
# It activates the virtual environment and runs pytest.

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

# Run the test suite
echo "Running the test suite..."
python -m pytest