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
        pe = request.args.get("pe")
        return render_template('delivery/delivery_create.html', pe=pe)
    except Exception as e :
        print(e)


@bp.route('/add', methods=["POST","GET"])
@login_required
def delivery_add():
    try :
        pe = request.form['pe']
        driver = request.form['driver']
        vehicle = request.form['vehicle']
        date = request.form['date']
        destination = request.form['destination']
        note = request.form['note']
        do_name = generate_unique_sequence_number(DeliveryOrder, DeliveryOrder.name, length=8, prefix="DO-")
        today_datetime = datetime.now()
        new_do = DeliveryOrder(name=do_name,purchase_event_id=int(pe),driver=driver,vehicle_number=vehicle, created=today_datetime,date=date,destination=destination,note=note)
        db.session.add(new_do)
        db.session.commit()
        return redirect(f"/delivery/index?pe={pe}")
    except Exception as e :
        print(e)
        return jsonify(status=400, text=5555555)


@bp.route('/edit', methods=["POST","GET"])
@login_required
def delivery_edit():
    try :
        do = request.args.get("do")
        pe = request.args.get("pe")
        delivery_order = DeliveryOrder.query.get(int(do))
        return render_template('delivery/delivery_edit.html', do=delivery_order, pe=pe)
    except Exception as e :
        print(e)
        return jsonify(status=400, text=5555555)

@bp.route('/update', methods=["POST","GET"])
@login_required
def delivery_update():
    try :
        pe = request.form['pe']
        do = request.form['do']
        vehicle = request.form['vehicle']
        driver = request.form['driver']
        date = request.form['date']
        destination = request.form['destination']
        note = request.form['note']
        delivery_order = DeliveryOrder.query.get(int(do))
        today_datetime = datetime.now()

        delivery_order.driver = driver
        delivery_order.vehicle_number = vehicle
        delivery_order.modified = today_datetime
        delivery_order.date = date
        delivery_order.destination = destination
        delivery_order.note = note
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
    delivery_order = DeliveryOrder.query.get(int(do))
    return render_template('delivery/delivery_detail.html', do=do, order_line=order_line, DeliveryOrder=DeliveryOrder, ProductOdoo=ProductOdoo, delivery_order=delivery_order)

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

@bp.route('/letter', methods=["GET","POST"])
@login_required
def delivery_letter():
    do = request.args.get('do')
    delivery_order = DeliveryOrder.query.get(int(do))
    order_line = PurchaseOrderLine.query.filter_by(delivery_order_id=delivery_order.id).all()

    return render_template('delivery/delivery_letter.html', delivery_order=delivery_order, order_line=order_line)




