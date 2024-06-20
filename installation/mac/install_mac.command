#!/bin/bash

cd "$(dirname "$0")" || exit

if ! command -v python3.10 &> /dev/null; then
    echo "Installing Python 3.10..."
    curl -O https://www.python.org/ftp/python/3.10.11/python-3.10.11-macos11.pkg
    sudo installer -pkg python-3.10.11-macos11.pkg -target /

    if ! command -v python3.10 &> /dev/null; then
        echo "Failed to install Python 3.10"
        exit 1
    else
        echo "Python 3.10 successfully installed."
    fi
else
    echo "Python 3.10 is already installed."
fi

if [ -d "../../venv" ]; then
    echo "Virtual environment already exists."
else
    echo "Creating virtual environment..."
    python3.10 -m venv ../../venv
    echo "Successfully created virtual environment."
fi

echo "Installing dependencies..."
source ../../venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r ../../data/requirements.txt
echo "Successfully installed dependencies."

echo "You can now run run_mac.sh to run the app."
