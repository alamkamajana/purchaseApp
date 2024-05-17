from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import requests
from app.models.models_odoo import ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, ResUserOdoo, NfcappCommodityOdoo, NfcappCommodityItemOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.db import db
from .auth import login_required

load_dotenv()
bp = Blueprint('data', __name__, url_prefix='/data')
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')


@bp.route('/sync', methods=["GET"])
@login_required
def sync_menu():
    return render_template('data/sync.html')

@bp.route('/master', methods=["GET"])
@login_required
def master_data():
    return render_template('data/master.html')