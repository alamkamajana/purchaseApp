import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlalchemy import and_, create_engine

from flask import jsonify
from app.models.db import db
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route("/login") 
def login(): 
    return render_template('auth/login.html')