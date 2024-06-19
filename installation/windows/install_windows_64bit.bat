@echo off

cd /d %~dp0

REM Define the Python version
set python_version=3.10.11

REM Define the installation directory
set install_dir=C:\Python\%python_version%

if exist "%install_dir%\python.exe" (
    echo Python %python_version% is already installed.
) else (
    echo Downloading Python %python_version%...
    curl -o python-installer.exe https://www.python.org/ftp/python/%python_version%/python-%python_version%-amd64.exe
    echo .
    echo Installing Python %python_version%, please wait...
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 DefaultAllUsersTargetDir="%install_dir%"
    echo Successfully installed Python %python_version%.
)

REM Check if virtual environment is already created
if exist "..\..\venv" (
    echo Virtual environment already exists.
) else (
    echo Creating virtual environment...
    "%install_dir%\python.exe" -m venv ..\..\venv
    echo Successfully created virtual environment.
)

REM Activate virtual environment and install dependencies
echo Installing dependencies...
call ..\..\venv\Scripts\activate.bat
..\..\venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
pip install -r ..\..\data\requirements.txt
echo Successfully installed dependencies.

echo You can now run run_windows.bat to run the app.
pause
