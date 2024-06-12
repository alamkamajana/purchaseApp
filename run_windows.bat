@echo off
echo Running the app...

REM set ip address
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4 Address"') do set ip=%%i
set ip=%ip:~1%

cd /d %~dp0
call venv\Scripts\activate
set FLASK_APP=run.py

start "" https://%ip%:5000/server/sync
python run.py
pause
