#!/bin/bash

echo "Running the app..."

# Set IP address
ip=$(ifconfig | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}')
echo "Detected IP address: $ip"

cd "$(dirname "$0")" || exit
source venv/bin/activate
export FLASK_APP=run.py

# Open the URL in the default browser
open "https://$ip:5001" &
python3.10 run.py
read -rp "Press any key to continue..."   # Pause the script until a key is pressed
