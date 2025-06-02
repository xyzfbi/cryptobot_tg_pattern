@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%

REM MODULE REPO URL AND DIR!!
set REPO_URL=https://github.com/xyzfbi/cryptobot_tg_pattern
set REPO_DIR=cryptobot_tg

REM MODULE CHECK CONDA
if not defined CONDA (
    set "CONDA=%USERPROFILE%\Miniconda3"
    if not exist "%CONDA%\Scripts\activate.bat" (
        set "CONDA=%USERPROFILE%\Anaconda3"
    )
)

if not exist "%CONDA%\Scripts\activate.bat" (
    echo ERROR: Conda not found at %CONDA%. Please set the correct CONDA path.
    pause
    exit /b 1
)

REM CHECK GIT
where git >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH. Please install Git from https://git-scm.com/download/win
    pause
    exit /b 1
)

REM MODULE CLONING
if not exist "%REPO_DIR%" (
    echo Cloning repository from %REPO_URL%
    git clone %REPO_URL% %REPO_DIR%
    if errorlevel 1 (
        echo ERROR: Failed to clone repository.
        pause
        exit /b 1
    )
) else (
    echo Repository already exists in %REPO_DIR%
)
REM GET INTO PROJECT DIR
cd /d "%REPO_DIR%"

REM ACTIVATE CONDA
call "%CONDA%\Scripts\activate.bat"

REM CHECK FOR ENVIRONMENT
conda env list | findstr /C:"cryptobot_tg" >nul
if errorlevel 1 (
    echo Creating Conda environment 'cryptobot_tg' from environment.yml
    call conda env create -f environment.yml
    if errorlevel 1 (
        echo ERROR: Failed to create Conda environment.
        pause
        exit /b 1
    )
) else (
    echo Environment 'cryptobot_tg' already exists
)

call conda activate cryptobot_tg
if errorlevel 1 (
    echo ERROR: Failed to activate Conda environment 'cryptobot_tg'.
    pause
    exit /b 1
)
REM MODULE START MAIN.PY
python main.py
if errorlevel 1 (
    echo ERROR: Failed to run main.py.
    pause
    exit /b 1
)
pause
