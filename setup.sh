#!/bin/bash

# setup.sh - Automates setup of virtual environment, dependencies, C++ build, and optional unit tests.

echo "Creating virtual environment..."
python3 -m venv venv || { echo "Failed to create virtualenv"; exit 1; }

echo "Activating environment..."
source venv/bin/activate || { echo "Failed to activate virtualenv"; exit 1; }

echo "Installing required packages..."
pip install --upgrade pip
pip install -r requirements.txt || { echo "Dependency installation failed"; exit 1; }

echo "Building C++ extension..."
python setup.py build_ext --inplace || { echo "C++ extension build failed"; exit 1; }

# Optional: run tests
export PYTHONPATH=.
if [[ "$1" == "--test" ]]; then
    echo "Running unit tests..."
    pip install pytest
    pytest tests || { echo "Tests failed"; exit 1; }
    echo "All tests passed!"
fi

echo "Setup complete."
echo "To activate your environment: source venv/bin/activate and then run the main.py as mentioned in README.md"
