@echo off

if not exist venv\ (
    echo creating virtual environment
    python -m venv venv
    echo installing dependencies
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo pip failed to install required dependencies
        deactivate
        rmdir /Q /S venv
        exit /b
    )
)

call venv\Scripts\activate.bat
call python.exe main.py %*
deactivate
