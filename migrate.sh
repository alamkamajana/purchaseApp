#!/bin/bash

# Activate the virtual environment
#source venv3/bin/activate

# Initialize the database migrations folder
flask --app run db init

# Generate the migration file
flask --app run db migrate -m "Update flaskApp"

# Apply the migrations to the database
flask --app run db upgrade

# Deactivate the virtual environment
deactivate
