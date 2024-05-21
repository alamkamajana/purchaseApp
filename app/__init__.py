# app/__init__.py
from flask import Flask
from .models import db, User
from .routes import bp as routes_bp
from dotenv import load_dotenv
import os
import requests
from . import models
from flask_migrate import Migrate
from flask_login import LoginManager




load_dotenv()
postgresql_url = os.getenv('POSTGRESQL_URL')
secret_key = os.getenv('SECRET_KEY')


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"{postgresql_url}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = secret_key

    db.init_app(app)
    migrate = Migrate(app, db)

    with app.app_context():
        db.create_all()  # Create sql tables for our data models

    app.register_blueprint(routes_bp)

    return app
