import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlalchemy import and_, create_engine
from flask import jsonify
from app.models.db import db
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.models_odoo import ResUserOdoo, ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, NfcappCommodityItemOdoo, NfcappCommodityOdoo
from app.models.models import PurchaseEvent, User, PurchaseOrder, PurchaseOrderLine
from functools import wraps
import socket
import requests
from datetime import datetime
import os
import uuid
import re
from .auth import login_required
import ast
import random
import string
import socket
from dotenv import load_dotenv

load_dotenv()
bp = Blueprint('server', __name__,url_prefix='/server')
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')

def generate_unique_sequence_number(model, column, length=8, prefix=""):
    sequence_number = prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    if not model.query.filter(column == sequence_number).first():
        return sequence_number

def get_current_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

@bp.route('/sync', methods=["GET"])
@login_required
def sync_menu():
    return render_template('server/sync.html')

@bp.route('/master/farmer', methods=["GET"])
@login_required
def master_data_farmer():
    parent_id = request.args.get('parent_id', type=int)
    farmers = NfcappFarmerOdoo.query.filter_by(parent_id=parent_id).all()
    print(farmers)
    datas = []
    for farmer in farmers:
        data = {}
        data['farmer']=farmer
        data2 = []
        commodity_items = NfcappCommodityItemOdoo.query.filter_by(farmer_id=farmer.odoo_id).all()
        for commodity_item in commodity_items:
            data2.append(commodity_item)
        data['commodity_items'] = data2
        datas.append(data)

    return render_template('server/master_farmer.html',datas=datas)


@bp.route('/master/purchase-order', methods=["GET"])
@login_required
def master_data_purchase_order():
    user = session['user_odoo_id']
    user_odoo = User.query.filter_by(user_odoo_id=int(user)).first()
    purchase_orders = PurchaseOrderOdoo.query.order_by(PurchaseOrderOdoo.odoo_id.desc()).all()
    purchase_orders2 = user_odoo.purchase_orders if user else []

    data = []
    for po in purchase_orders2 :
        po_json = {}
        po_json['id'] = po.id
        po_json['name'] = po.name
        data.append(po_json)
        po_order_line = PurchaseOrderLineOdoo.query.filter_by(order_id=int(po.odoo_id)).all()
        po_order_line_arr = []
        for order_line in po_order_line :
            order_line_json = {}
            order_line_json['product_name'] = order_line.product_name
            order_line_json['price_unit'] = order_line.price_unit
            order_line_json['product_qty'] = order_line.product_qty
            po_order_line_arr.append(order_line_json)
        po_json['order_line'] = po_order_line_arr
    return render_template('server/master_po.html',purchase_data=data)


@bp.route('/purchase-event', methods=["GET"])
@login_required
def purchase_event_list():
    device_name = os.environ.get('USER')
    mac_addr = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    local_ip_address = socket.gethostbyname(socket.gethostname())
    external_ip_address = requests.get('https://api.ipify.org').text
    po_list = PurchaseOrderOdoo.query.all()
    user_list = ResUserOdoo.query.all()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = PurchaseEvent.query.order_by(PurchaseEvent.id.desc()).paginate(page=page, per_page=per_page,
                                                                                error_out=False)
    events = pagination.items
    total_pages = pagination.pages
    users = User.query.all()
    user = session['user_odoo_id']
    user_odoo = User.query.filter_by(user_odoo_id=int(user)).first()
    # purchase_orders = PurchaseOrderOdoo.query.order_by(PurchaseOrderOdoo.odoo_id.desc()).all()
    purchase_orders = user_odoo.purchase_orders if user else []
    # events = PurchaseEvent.query.order_by(PurchaseEvent.id).all()
    base_url = request.url_root
    return render_template('server/purchase_event.html', events=events, users=users, page=page, total_pages=total_pages,
                           po_list=purchase_orders, user_list=user_list, device_name=device_name, base_url=base_url)


@bp.route('/purchase-event/add', methods=["POST"])
@login_required
def purchase_event_add():
    fund = request.form['fund']
    ics = request.form['ics']
    ap_name = request.form['ap-name']
    purchaser_id = request.form['purchaser']
    cashier_id = request.form['cashier']
    purchase_order_odoo_id = request.form['purchase-order']
    pe_name = generate_unique_sequence_number(PurchaseEvent, PurchaseEvent.name, length=8, prefix="")

    purchase_event = PurchaseEvent(name=pe_name,fund=fund, ics=ics, purchaser_id=purchaser_id, cashier_id=cashier_id,
                                   purchase_order_odoo_id=purchase_order_odoo_id, ap_name=ap_name)
    db.session.add(purchase_event)
    db.session.commit()

    return redirect(url_for('routes.server.purchase_event_list'))

@bp.route('/purchase-event/update', methods=["POST"])
@login_required
def purchase_event_update():
    # Retrieve updated data from the POST request
    id = request.form['event']
    po_id = request.form['purchase-order']
    purchaser_id = request.form['purchaser']
    cashier_id = request.form['cashier']
    ics = request.form['ics']
    ap_name = request.form['ap-name']
    fund = request.form['fund']

    # Update the data dictionary
    event = PurchaseEvent.query.filter_by(id=id).first()  # Example: Update the user with ID 1
    if event:
        event.purchase_order_odoo_id = po_id
        event.cashier_id = cashier_id
        event.purchaser_id = purchaser_id
        event.ics = ics
        event.ap_name = ap_name
        event.fund = fund

        db.session.commit()
        return redirect(request.referrer)
    else:
        return redirect(request.referrer)


