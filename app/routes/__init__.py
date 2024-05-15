# app/routes/__init__.py
from flask import Blueprint

bp = Blueprint('routes', __name__)

from .api_sync import *
from .api import *
