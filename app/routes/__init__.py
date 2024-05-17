# app/routes/__init__.py
from flask import Blueprint

bp = Blueprint('routes', __name__)

from .api import bp as api_bp
from .api_sync import bp as api_sync_bp
from .auth import bp as auth
from .data import bp as data_bp

bp.register_blueprint(api_bp)
bp.register_blueprint(api_sync_bp)
bp.register_blueprint(auth)
bp.register_blueprint(data_bp)