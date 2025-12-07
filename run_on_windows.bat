@echo off
echo ==========================================
echo VirtualAI Painter - Windows Launcher
echo ==========================================

cd /d "%~dp0"

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 'python' command not found. Trying 'py'...
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Error: Python is not installed or not in PATH.
        echo Please install Python from python.org
        pause
        exit /b
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

IF NOT EXIST "venv_win" (
    echo Creating virtual environment (isolated)...
    %PYTHON_CMD% -m venv venv_win
    if %errorlevel% neq 0 (
        echo Error creating venv.
        pause
        exit /b
    )
)

echo Activating virtual environment...
call venv_win\Scripts\activate

echo Installing Requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing requirements.
    pause
    exit /b
)

echo Starting Application...
python main.py
if %errorlevel% neq 0 (
    echo Application exited with error.
)

echo.
echo Application Closed.
pause
