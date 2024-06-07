@echo off

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Initialize the database migrations folder
flask --app run db init

REM Generate the migration file
flask --app run db migrate -m "Update purchaseApp"

REM Apply the migrations to the database
flask --app run db upgrade

REM Deactivate the virtual environment
deactivate
