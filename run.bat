@echo off

python main.py
IF %ERRORLEVEL% NEQ 0 (
    echo An error occurred. Attempting to install requirements...
    pip install -r requirements.txt
    echo Trying to run the script again...
    python main.py
)

