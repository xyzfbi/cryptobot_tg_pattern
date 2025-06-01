@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%

call "%CONDA%\Scripts\activate.bat"

conda env list | findstr /C:"cryptobot_tg" >nul
if errorlevel 1 (
    echo Creating Conda environment 'cryptobot_tg' from environment.yml
    conda env create -f environment.yml
) else (
    echo Environment 'cryptobot_tg' already exists
)

call conda activate cryptobotto_tg

python main.py
pause