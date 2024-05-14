# app/__init__.py
from flask import Flask
from .models import db
from .routes import bp as routes_bp
from dotenv import load_dotenv
import os
import requests
from . import models
from flask_migrate import Migrate



load_dotenv()
postgresql_url = os.getenv('POSTGRESQL_URL')


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"{postgresql_url}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    with app.app_context():
        db.create_all()  # Create sql tables for our data models

    app.register_blueprint(routes_bp)

    return app
