@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%

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

:: активируем кондочку
call "%CONDA%\Scripts\activate.bat"

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

python main.py
if errorlevel 1 (
    echo ERROR: Failed to run main.py.
    pause
    exit /b 1
)
pause