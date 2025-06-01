@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%

:: Укажи URL твоего репо на GitHub
set REPO_URL=https://github.com/xyzfbi/cryptobot_tg_pattern
:: Имя папки для клонирования (можно изменить)
set REPO_DIR=cryptobot_tg

:: Проверяем, определена ли переменная CONDA
if not defined CONDA (
    set "CONDA=%USERPROFILE%\Miniconda3"
    if not exist "%CONDA%\Scripts\activate.bat" (
        set "CONDA=%USERPROFILE%\Anaconda3"
    )
)

:: Проверяем наличие activate.bat
if not exist "%CONDA%\Scripts\activate.bat" (
    echo ERROR: Conda not found at %CONDA%. Please set the correct CONDA path.
    pause
    exit /b 1
)

:: Проверяем наличие Git
where git >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH. Please install Git from https://git-scm.com/download/win
    pause
    exit /b 1
)

:: Проверяем, существует ли папка репо, и клонируем, если нет
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

:: Переходим в папку репо
cd /d "%REPO_DIR%"

:: Проверяем наличие run_bot.bat
if not exist "run_bot.bat" (
    echo ERROR: run_bot.bat not found in %REPO_DIR%.
    pause
    exit /b 1
)

:: Активируем Conda
call "%CONDA%\Scripts\activate.bat"

:: Проверяем наличие окружения cryptobot_tg
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

:: Активируем окружение
call conda activate cryptobot_tg
if errorlevel 1 (
    echo ERROR: Failed to activate Conda environment 'cryptobot_tg'.
    pause
    exit /b 1
)

:: Запускаем run_bot.bat
call run_bot.bat
if errorlevel 1 (
    echo ERROR: Failed to run run_bot.bat.
    pause
    exit /b 1
)

:: Пауза для отладки (убери, если не нужна)
pause
