@echo off
setlocal
set PYTHON_EXE=c:\Users\MP2NE93D\miniconda3\python.exe

:menu
cls
echo 🌐 GLU-STOCK: PC COMMAND CENTER (v11.0)
echo ------------------------------------------
echo [1] Setup Environment (Install/Update)
echo [2] Unified Training (Brain RF + CNN)
echo [3] Run Backtest Lab (Strategy Validation)
echo [4] Start Telegram Bot (PC Side Monitoring)
echo [Q] Quit
echo ------------------------------------------
set /p choice="Pilih menu sayang (1-4/Q): "

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto train
if "%choice%"=="3" goto backtest
if "%choice%"=="4" goto bot
if /i "%choice%"=="Q" exit /b

:setup
echo.
echo [INFO] Updating Environment...
if not exist "pc_venv" "%PYTHON_EXE%" -m venv pc_venv
call pc_venv\Scripts\activate.bat
python -m pip install -r requirements.txt
echo [SUCCESS] Setup Complete!
pause
goto menu

:train
echo.
echo [INFO] Starting Unified Intelligence Training...
call pc_venv\Scripts\activate.bat
python train_intel.py
echo [SUCCESS] Training Complete! Check data/models/
pause
goto menu

:backtest
echo.
echo [INFO] Starting Backtest Lab...
call pc_venv\Scripts\activate.bat
python scheduler.py --backtest
pause
goto menu

:bot
echo.
echo [INFO] Starting Telegram Bot...
call pc_venv\Scripts\activate.bat
python telegram_bot.py
pause
goto menu
