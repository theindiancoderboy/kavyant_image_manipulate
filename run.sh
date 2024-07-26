#!/bin/bash
python3 main.py
if [ $? -ne 0 ]; then
    echo "An error occurred. Attempting to install requirements..."
    python3 -m pip install -r requirements.txt
    echo "Trying to run the script again..."
    python3 main.py
fi
