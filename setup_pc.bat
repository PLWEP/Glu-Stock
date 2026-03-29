@echo off
setlocal

echo 🌐 GLU-STOCK: PC Intelligence Setup (v1.0)
echo ------------------------------------------

:: 1. Check Python installation
set PYTHON_EXE=c:\Users\MP2NE93D\miniconda3\python.exe
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found at %PYTHON_EXE%
    echo Please check your miniconda path.
    exit /b 1
)

:: 2. Create Virtual Environment
if not exist "pc_venv" (
    echo [INFO] Creating Virtual Environment 'pc_venv'...
    "%PYTHON_EXE%" -m venv pc_venv
) else (
    echo [INFO] Virtual Environment 'pc_venv' already exists.
)

:: 3. Install Dependencies
echo [INFO] Installing/Updating dependencies from requirements.txt...
call pc_venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

:: 4. Create Directories
if not exist "data\models" (
    mkdir "data\models"
)
if not exist "logs" (
    mkdir "logs"
)

echo.
echo ✅ SETUP COMPLETE! 💹
echo ------------------------------------------
echo Untuk mulai melatih otak (Training), jalankan:
echo call pc_venv\Scripts\activate.bat
echo python utils/ml_trainer_pc.py
echo.
pause
