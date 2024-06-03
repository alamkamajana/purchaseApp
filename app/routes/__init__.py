# app/routes/__init__.py
from flask import Blueprint

bp = Blueprint('routes', __name__)

from .auth import bp as auth_bp
from .server import bp as server_bp
from .sync import bp as sync_bp
from .purchase import bp as purchase_bp
from .cashier import bp as cashier_bp
from .delivery import bp as delivery_bp
from .upload import bp as upload_bp

bp.register_blueprint(server_bp)
bp.register_blueprint(auth_bp)
bp.register_blueprint(sync_bp)
bp.register_blueprint(purchase_bp)
bp.register_blueprint(cashier_bp)
bp.register_blueprint(delivery_bp)
bp.register_blueprint(upload_bp)
