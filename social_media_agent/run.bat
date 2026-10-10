@echo off
REM ================================================================
REM  run.bat — Windows Launcher for SocialMind AI
REM  Social Media Agentic AI · IBM Granite LLM · watsonx.ai
REM ================================================================
REM  Usage: Double-click this file OR run from Command Prompt:
REM         cd social_media_agent && run.bat
REM ================================================================

title SocialMind AI — IBM Granite LLM

echo.
echo  ============================================================
echo   SocialMind AI — Social Media Agentic AI
echo   Powered by IBM Granite LLM via IBM watsonx.ai
echo  ============================================================
echo.

REM ── Step 1: Check Python is installed ──────────────────────────
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Python is not installed or not in your PATH.
    echo.
    echo  Please install Python 3.10 or newer from:
    echo  https://www.python.org/downloads/
    echo.
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

FOR /F "tokens=2 delims= " %%V IN ('python --version 2^>^&1') DO SET PYVER=%%V
echo  [OK] Python %PYVER% found.

REM ── Step 2: Create virtual environment if it doesn't exist ─────
IF NOT EXIST "venv\" (
    echo.
    echo  [SETUP] Creating virtual environment...
    python -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  [OK] Virtual environment created.
)

REM ── Step 3: Activate virtual environment ───────────────────────
echo.
echo  [SETUP] Activating virtual environment...
call venv\Scripts\activate.bat
IF %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo  [OK] Virtual environment activated.

REM ── Step 4: Install / upgrade dependencies ─────────────────────
echo.
echo  [SETUP] Installing dependencies from requirements.txt...
pip install -r requirements.txt --quiet --upgrade
IF %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Failed to install dependencies.
    echo  Try running:  pip install -r requirements.txt
    pause
    exit /b 1
)
echo  [OK] Dependencies installed.

REM ── Step 5: Check .env file ────────────────────────────────────
echo.
IF NOT EXIST ".env" (
    echo  [NOTICE] No .env file found.
    echo  Copying .env.example to .env...
    copy .env.example .env >nul
    echo.
    echo  ╔══════════════════════════════════════════════════════╗
    echo  ║  ACTION REQUIRED — Configure your IBM credentials   ║
    echo  ╠══════════════════════════════════════════════════════╣
    echo  ║  Edit .env and set:                                  ║
    echo  ║    WATSONX_API_KEY      = your IBM Cloud API key     ║
    echo  ║    WATSONX_PROJECT_ID   = your watsonx.ai project ID ║
    echo  ║    WATSONX_URL          = your region endpoint       ║
    echo  ║                                                      ║
    echo  ║  The app will still run in DEMO MODE without these.  ║
    echo  ╚══════════════════════════════════════════════════════╝
    echo.
) ELSE (
    echo  [OK] .env file found.
)

REM ── Step 6: Launch the Flask application ───────────────────────
echo.
echo  [START] Launching SocialMind AI...
echo.
echo  ┌──────────────────────────────────────────────┐
echo  │  Open your browser and go to:               │
echo  │  http://127.0.0.1:5000                      │
echo  │                                              │
echo  │  Press CTRL+C in this window to stop.       │
echo  └──────────────────────────────────────────────┘
echo.

python app.py

REM ── If Flask exits, pause so the user can see any errors ───────
echo.
echo  [INFO] Application has stopped.
pause
