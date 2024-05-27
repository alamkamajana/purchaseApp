from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import requests
from app.models.models_odoo import ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, ResUserOdoo, NfcappCommodityOdoo, NfcappCommodityItemOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.db import db
from app.models.models import User, PurchaseOrder, PurchaseEvent, DeliveryOrder, PurchaseOrderLine
from .auth import login_required
import ast
from flask import jsonify
import random
import string
from datetime import datetime

load_dotenv()
bp = Blueprint('delivery', __name__, url_prefix='/delivery')
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')

def generate_unique_sequence_number(model, column, length=8, prefix=""):
    sequence_number = prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    if not model.query.filter(column == sequence_number).first():
        return sequence_number
@bp.route('/index', methods=["GET"])
@login_required
def delivery_index():
    pe = request.args.get("pe")
    purchase_event = PurchaseEvent.query.filter_by(id=int(pe)).first()

    pe_list = PurchaseEvent.query.all()
    do_list = DeliveryOrder.query.filter_by(purchase_event_id=int(pe))
    return render_template('delivery/delivery.html', pe_list=pe_list, do_list=do_list, pe=purchase_event)

@bp.route('/create', methods=["POST","GET"])
@login_required
def delivery_create():
    try :
        pe = request.args.get('pe')
        # driver = request.args.get('driver')
        # vehicle_number = request.args.get('vehicle_number')
        do_name = generate_unique_sequence_number(DeliveryOrder, DeliveryOrder.name, length=8, prefix="DO-")
        today_datetime = datetime.now()
        #
        current_user_session = session['user_odoo_id']
        current_user = User.query.filter_by(user_odoo_id=int(current_user_session) if current_user_session else None).first()
        new_do = DeliveryOrder(name=do_name,purchase_event_id=int(pe), created=today_datetime, create_uid=current_user.id if current_user else None)
        db.session.add(new_do)
        db.session.commit()
        return redirect(f"/delivery/index?pe={pe}")
    except Exception as e :
        print(e)
        return jsonify(status=400, text=5555555)


@bp.route('/detail', methods=["GET"])
@login_required
def delivery_detail():
    do = request.args.get("do")
    order_line = PurchaseOrderLine.query.filter_by(delivery_order_id=int(do)).all()
    return render_template('delivery/delivery_detail.html', do=do, order_line=order_line, DeliveryOrder=DeliveryOrder, ProductOdoo=ProductOdoo)

@bp.route('/detail/delete', methods=["GET"])
@login_required
def delivery_detail_delete():
    order_line = request.args.get("order_line")
    print(order_line)
    order_line = PurchaseOrderLine.query.get(int(order_line))
    if order_line:
        order_line.delivery_order_id = None
        db.session.commit()
    return redirect(request.referrer)

@bp.route('/delete', methods=["GET"])
@login_required
def delivery_delete():
    do = request.args.get("do")
    delivery_order = DeliveryOrder.query.get(int(do))
    db.session.delete(delivery_order)
    db.session.commit()
    return redirect(request.referrer)

@bp.route('/detail/add', methods=["GET","POST"])
@login_required
def delivery_detail_add():
    do = request.form['do']
    barcode = request.form['barcode']

    delivery_order = DeliveryOrder.query.filter_by(id=int(do)).first()
    order_line = PurchaseOrderLine.query.filter_by(barcode=barcode).first()

    if order_line :
        order_line.delivery_order_id = delivery_order.id
        db.session.commit()

    return redirect(f"/delivery/detail?do={delivery_order.id}")





