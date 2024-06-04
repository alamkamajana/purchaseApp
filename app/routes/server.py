import functools

import psutil
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
import socket
from sqlalchemy import and_, create_engine
from flask import jsonify
from app.models.db import db
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.models_odoo import ResUserOdoo, ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, NfcappCommodityItemOdoo, NfcappCommodityOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.models import PurchaseEvent, User, PurchaseOrder, PurchaseOrderLine, Money
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
import qrcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64


load_dotenv()
bp = Blueprint('server', __name__,url_prefix='/server')
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')

def get_local_ip():
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Connect to an external server (Google DNS)
        s.connect(('8.8.8.8', 80))
        # Get the local IP address
        local_ip = s.getsockname()[0]
    except Exception as e:
        # Handle exception and provide fallback
        local_ip = '127.0.0.1'
    finally:
        # Close the socket
        s.close()

    return local_ip

def generate_qr_code(data):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill='black', back_color='white')

    # Save the image to a BytesIO object
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    # Encode the image to base64
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_str


def generate_unique_sequence_number(model, column, length=8, prefix=""):
    sequence_number = prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    if not model.query.filter(column == sequence_number).first():
        return sequence_number


def get_current_ip():
    ip_addresses = {}
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if address.family == socket.AF_INET:
                ip_addresses[interface_name] = address.address

    print(ip_addresses)
    return ip_addresses.get('en0')


@bp.route('/sync', methods=["GET"])
@login_required
def sync_menu():
    return render_template('server/sync.html')

@bp.route('/master/farmer', methods=["GET"])
@login_required
def master_data_farmer():
    parent_id = request.args.get('parent_id',0, type=int)
    station_id = request.args.get('station_id', 0 , type=int)
    farmers = NfcappFarmerOdoo.query.filter_by(parent_id=parent_id).all()
    clusters = NfcappClusterOdoo.query.all()
    stations = NfcappStationOdoo.query.all()
    datas = []
    for farmer in farmers:
        data = {}
        data['farmer']=farmer
        data2 = []
        commodity_items = NfcappCommodityItemOdoo.query.filter(
            NfcappCommodityItemOdoo.farmer_id == farmer.odoo_id,
            NfcappCommodityItemOdoo.product_id.isnot(None)
        ).all()
        for commodity_item in commodity_items:
            data2.append(commodity_item)
        data['commodity_items'] = data2
        datas.append(data)

    return render_template('server/master_farmer.html',datas=datas, clusters=clusters, stations=stations, parent_id=parent_id, station_id=station_id)


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
        po_json['po'] = po
        data.append(po_json)
        po_order_line = PurchaseOrderLineOdoo.query.filter_by(order_id=int(po.odoo_id)).all()
        po_order_line_arr = []
        for order_line in po_order_line :
            order_line_json = {}
            order_line_json['order_line'] = order_line
            po_order_line_arr.append(order_line_json)
        po_json['order_lines'] = po_order_line_arr
    return render_template('server/master_po.html',purchase_data=data)


@bp.route('/purchase-order/view', methods=["POST","GET"])
@login_required
def purchase_order_view():
    print(request)
    po_id = request.args.get("po")
    purchase_order = PurchaseOrderOdoo.query.get(po_id)
    return render_template('server/purchase_order_view.html', purchase_order=purchase_order)


@bp.route('/purchase-event/', methods=["GET"])
@login_required
def purchase_event_list():
    po_id = request.args.get('po', 0, type=int)
    events = PurchaseEvent.query.filter_by(purchase_order_odoo_id=po_id).all()
    purchase_order = PurchaseOrderOdoo.query.get(po_id)
    purchase_order_line = po_order_line = PurchaseOrderLineOdoo.query.filter_by(order_id=int(purchase_order.odoo_id)).all()
    event_ids = [event.id for event in events]
    orders = PurchaseOrder.query.filter(PurchaseOrder.purchase_event_id.in_(event_ids)).all()
    return render_template('server/purchase_event.html', events=events,po=po_id,purchase_order=purchase_order, orders=orders , purchase_order_line=purchase_order_line, NfcappFarmerOdoo=NfcappFarmerOdoo, ProductOdoo=ProductOdoo)



@bp.route('/purchase-event/create', methods=["POST","GET"])
@login_required
def purchase_event_create_new():
    po_id = request.args.get('po', 0, type=int)

    po_list = PurchaseOrderOdoo.query.filter_by(id=po_id).first()

    user_odoo = session['user_odoo_id']
    user = User.query.filter_by(user_odoo_id=user_odoo).first()
    return render_template('server/purchase_event_create.html', purchase_order=po_list)


@bp.route('/purchase-event/add', methods=["POST","GET"])
@login_required
def purchase_event_add():
    date = request.form['date']
    note = request.form['note']
    purchase_order = request.form['purchase-order']
    pe_name = generate_unique_sequence_number(PurchaseEvent, PurchaseEvent.name, length=8, prefix="PE-")
    today_datetime = datetime.now()
    date = datetime.strptime(date, '%Y-%m-%d').date()
    purchase_event = PurchaseEvent(name=pe_name, note=note,created=today_datetime, date_stamp=date,purchase_order_odoo_id=purchase_order)
    db.session.add(purchase_event)
    db.session.commit()

    return redirect(url_for('routes.server.purchase_event_view', pe=purchase_event.id))

@bp.route('/purchase-event/details', methods=["POST","GET"])
@login_required
def purchase_event_details():
    purchasers = ResUserOdoo.query.all()
    purchase_event_id = request.args.get("pe")
    purchase_event = PurchaseEvent.query.get(purchase_event_id)
    purchase_order = PurchaseOrderOdoo.query.get(purchase_event.purchase_order_odoo_id)
    return render_template('server/purchase_event_details.html', purchase_event=purchase_event, purchase_order=purchase_order)

@bp.route('/purchase-event/view', methods=["POST","GET"])
@login_required
def purchase_event_view():
    purchasers = ResUserOdoo.query.all()
    base_url = "https://"+str(get_current_ip())+":5000/"
    purchase_event_id = request.args.get("pe")
    purchase_event = PurchaseEvent.query.get(purchase_event_id)
    local_ip = get_local_ip()
    data_purchase = f"{base_url}purchase/transaction?pe={purchase_event_id}"
    data_delivery = f"{base_url}delivery/index?pe={purchase_event_id}"
    data_cashier = f"{base_url}cashier/index?pe={purchase_event_id}"
    qr_code_purchase = generate_qr_code(data_purchase)
    qr_code_delivery = generate_qr_code(data_delivery)
    qr_code_cashier = generate_qr_code(data_cashier)
    purchase_order = PurchaseOrderOdoo.query.get(purchase_event.purchase_order_odoo_id)

    payments = Money.query.filter_by(purchase_event_id=purchase_event.id).order_by(Money.created.asc())
    purchase_order_odoo = PurchaseOrderOdoo.query.get(purchase_event.purchase_order_odoo_id)
    return render_template('server/purchase_event_view.html', qr_code_cashier=qr_code_cashier,qr_code_delivery=qr_code_delivery,qr_code_purchase=qr_code_purchase,data_cashier=data_cashier,data_delivery=data_delivery,data_purchase=data_purchase,purchase_event=purchase_event,base_url=base_url, purchase_order=purchase_order,payments=payments, PurchaseOrder=PurchaseOrder,purchase_order_odoo=purchase_order_odoo)


@bp.route('/purchase-event/update', methods=["POST","GET"])
@login_required
def purchase_event_update():
    # Retrieve updated data from the POST request
    id = request.form['event_id']
    date = request.form['date_stamp']
    note = request.form['note']
    po = request.form['purchase-order']
    event = PurchaseEvent.query.filter_by(id=id).first()
    if event:
        event.note = note
        event.date_stamp = datetime.strptime(date, '%Y-%m-%d').date()
        event.purchase_order_odoo_id = int(po) if po else None
        db.session.commit()
        return redirect("/server/purchase-event/view?pe="+str(event.id))
    else:
        return redirect("/server/purchase-event/view?pe="+str(event.id))


@bp.route('/purchase-event/delete', methods=["POST","GET"])
@login_required
def purchase_event_delete():
    purchase_event_id = request.args.get("pe")
    print(purchase_event_id)

    # Retrieve the object from the database
    purchase_event = PurchaseEvent.query.get(purchase_event_id)

    if purchase_event:
        # Mark the object for deletion
        db.session.delete(purchase_event)

        # Commit the transaction to save the changes
        db.session.commit()

    return redirect(url_for('routes.server.purchase_event_list'))


@bp.route('/purchase-event/payments', methods=["POST","GET"])
@login_required
def purchase_event_payments():
    purchase_event_id = request.args.get("pe")
    purchase_event = PurchaseEvent.query.get(purchase_event_id)
    payments = Money.query.filter_by(purchase_event_id=purchase_event.id).order_by(Money.created.asc())
    purchase_order_odoo = PurchaseOrderOdoo.query.get(purchase_event.purchase_order_odoo_id)
    return render_template('server/purchase_event_payments.html', purchase_event=purchase_event, payments=payments, PurchaseOrder=PurchaseOrder,purchase_order_odoo=purchase_order_odoo)


@bp.route('/money/add', methods=["POST","GET"])
@login_required
def server_money_add():
    try :
        purchase_event_id = request.form.get('purchase_event_id')
        purchase_order_id = request.form.get('purchase_order_id')
        amount = request.form.get('amount')
        type = request.form.get('type')
        note = request.form.get('note')
        amount = float(amount)
        if type.lower() == 'credit' :
            amount = -amount

        purchase_event_id = int(purchase_event_id)
        money_name = generate_unique_sequence_number(Money, Money.number, length=8, prefix="MO-")
        today_datetime = datetime.now()
        current_user_session = session['user_odoo_id']
        current_user = User.query.filter_by(
            user_odoo_id=int(current_user_session) if current_user_session else None).first()
        money = Money(amount=amount,note=note,purchase_event_id=purchase_event_id,number=money_name,purchase_order_id=purchase_order_id if purchase_order_id else None, created = today_datetime, create_uid=current_user.id if current_user else None)
        print(money)
        db.session.add(money)
        db.session.commit()
        return redirect(request.referrer)
    except Exception as e :
        print(e)

@bp.route('/money/add2', methods=["GET"])
@login_required
def server_money_add2():
    try :
        purchase_event_id = request.args.get('purchase_event_id')
        purchase_order_id = request.args.get('purchase_order_id')
        amount = request.args.get('amount')
        type = request.args.get('type')
        note = request.args.get('note')
        amount = float(amount)
        if type.lower() == 'credit' :
            amount = -amount

        purchase_event_id = int(purchase_event_id)
        money_name = generate_unique_sequence_number(Money, Money.number, length=8, prefix="MO-")
        today_datetime = datetime.now()
        current_user_session = session['user_odoo_id']
        current_user = User.query.filter_by(
            user_odoo_id=int(current_user_session) if current_user_session else None).first()
        money = Money(amount=amount,note=note,purchase_event_id=purchase_event_id,number=money_name,purchase_order_id=purchase_order_id if purchase_order_id else None, created = today_datetime, create_uid=current_user.id if current_user else None)
        print(money)
        db.session.add(money)
        db.session.commit()
        return redirect(request.referrer)
    except Exception as e :
        print(e)

@bp.route('/test-print', methods=["GET"])
def server_test_print():
    return render_template('server/test_print.html')



