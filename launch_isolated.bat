@echo off
TITLE VirtualAI Painter Launcher
echo ==========================================
echo VirtualAI Painter - Isolated Launcher
echo ==========================================

cd /d "%~dp0"
echo Current Directory: %CD%

:: 1. Check Python
echo.
echo [1/4] Checking Python...
python --version 2>NUL
IF %ERRORLEVEL% NEQ 0 (
    echo 'python' not found. Checking 'py' launcher...
    py --version 2>NUL
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python not found! Please install Python from python.org.
        pause
        exit /b
    )
    set PY=py
) ELSE (
    set PY=python
)
echo Using: %PY%

:: 2. Create Venv
echo.
echo [2/4] Setting up Virtual Environment (venv_isolate)...
IF NOT EXIST "venv_isolate" (
    %PY% -m venv venv_isolate
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create venv.
        pause
        exit /b
    )
    echo Created new venv.
) ELSE (
    echo Found existing venv.
)

:: 3. Install Dependencies
echo.
echo [3/4] Installing Requirements...
call venv_isolate\Scripts\activate.bat
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b
)

:: 4. Run App
echo.
echo [4/4] Starting Application...
python main.py
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [APP ERROR] The application crashed or exited with an error.
)

echo.
echo Closing in 10 seconds...
timeout /t 10
