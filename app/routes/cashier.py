from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import requests
from app.models.models_odoo import ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, ResUserOdoo, NfcappCommodityOdoo, NfcappCommodityItemOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.db import db
from app.models.models import User, PurchaseOrder
from .auth import login_required
import ast
from flask import jsonify

load_dotenv()
bp = Blueprint('cashier', __name__, url_prefix='/cashier')
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')


@bp.route('/index', methods=["GET"])
@login_required
def cashier_index():
    return render_template('cashier/cashier.html')


@bp.route('/search/po', methods=["GET","POST"])
@login_required
def cashier_search_po():
    if request.method.lower() == 'post' :
        po = request.form['po']
    else :
        po = request.args.get('po')
    purchase_order = PurchaseOrder.query.filter_by(name=po).first()
    return jsonify({'po': purchase_order.id if purchase_order else None})

@bp.route('/po/detail', methods=["GET"])
@login_required
def cashier_po_detail():
    try :
        po = request.args.get('po')
        purchase_order = PurchaseOrder.query.filter_by(id=int(po)).first()
        return render_template('cashier/po_details.html', purchase_order=purchase_order)
    except Exception as e :
        print(e)

@bp.route('/payment/add', methods=["GET"])
@login_required
def cashier_payment_add():
    try :
        po = request.args.get('po')
        purchase_order = PurchaseOrder.query.filter_by(id=int(po)).first()
        return redirect(request.referrer)
    except Exception as e :
        print(e)
