import app
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import requests
from app.models.models_odoo import ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, ResUserOdoo, NfcappCommodityOdoo, NfcappCommodityItemOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.db import db
from app.models.models import User, PurchaseOrder, PurchaseEvent, DeliveryOrder, PurchaseOrderLine
import ast
from flask import jsonify
import random
import string
from datetime import datetime
from sqlalchemy import and_

load_dotenv()
bp = Blueprint('delivery', __name__, url_prefix='/delivery')
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')

def generate_unique_sequence_number(model, column, length=8, prefix=""):
    sequence_number = prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    if not model.query.filter(column == sequence_number).first():
        return sequence_number
@bp.route('/index', methods=["GET"])

def delivery_index():
    pe = request.args.get("pe")
    purchase_event = PurchaseEvent.query.filter_by(id=int(pe)).first()

    pe_list = PurchaseEvent.query.all()
    do_list = DeliveryOrder.query.filter_by(purchase_event_id=int(pe)).order_by(DeliveryOrder.id.desc()).all()
    return render_template('delivery/delivery.html', pe_list=pe_list, do_list=do_list, pe=purchase_event)

@bp.route('/create', methods=["POST","GET"])

def delivery_create():
    try :
        pe = request.args.get("pe")
        return render_template('delivery/delivery_create.html', pe=pe)
    except Exception as e :
        print(e)


@bp.route('/add', methods=["POST","GET"])
def delivery_add():
    try :
        pe = request.form['pe']
        driver = request.form['driver']
        vehicle = request.form['vehicle']
        sent_date = datetime.strptime(request.form['sent_date'], '%Y-%m-%dT%H:%M')
        received_date = datetime.strptime(request.form['received_date'], '%Y-%m-%dT%H:%M')
        origin = request.form['origin']
        destination = request.form['destination']
        note = request.form['note']
        status = "Draft"
        purchase_event = PurchaseEvent.query.get(int(pe))
        do_name = generate_unique_sequence_number(DeliveryOrder, DeliveryOrder.name, length=4, prefix=purchase_event.name+"-")
        today_datetime = datetime.now()
        new_do = DeliveryOrder(name=do_name,purchase_event_id=int(pe),driver=driver,vehicle_number=vehicle, created=today_datetime,sent_date=sent_date, received_date=received_date,origin=origin,destination=destination,note=note, status=status)
        db.session.add(new_do)
        db.session.commit()
        return redirect(f"/delivery/detail?do={new_do.id}")
    except Exception as e :
        print(e)
        return jsonify(status=400, text=5555555)


@bp.route('/edit', methods=["POST","GET"])
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

def delivery_update():
    try :
        pe = request.form['pe']
        do = request.form['do']
        vehicle = request.form['vehicle']
        driver = request.form['driver']
        sent_date = datetime.strptime(request.form['sent_date'], '%Y-%m-%dT%H:%M')
        received_date = datetime.strptime(request.form['received_date'], '%Y-%m-%dT%H:%M')
        origin = request.form['origin']
        destination = request.form['destination']
        note = request.form['note']
        delivery_order = DeliveryOrder.query.get(int(do))
        today_datetime = datetime.now()

        delivery_order.driver = driver
        delivery_order.vehicle_number = vehicle
        delivery_order.modified = today_datetime
        delivery_order.sent_date = sent_date
        delivery_order.received_date = received_date
        delivery_order.origin = origin
        delivery_order.destination = destination
        delivery_order.note = note
        db.session.commit()
        return redirect(f"/delivery/detail?do={do}")
    except Exception as e :
        print(e)
        return jsonify(status=400, text=5555555)

@bp.route('/confirm', methods=["POST","GET"])
def delivery_confirm():
    delivery_order_id = request.args.get('do')
    do = DeliveryOrder.query.filter_by(id=int(delivery_order_id)).first()
    do.status = 'Confirm'
    db.session.commit()
    return redirect(request.referrer)

@bp.route('/reset', methods=["POST","GET"])
def delivery_reset():
    delivery_order_id = request.args.get('do')
    do = DeliveryOrder.query.filter_by(id=int(delivery_order_id)).first()
    do.status = 'Draft'
    db.session.commit()
    return redirect(request.referrer)


@bp.route('/detail', methods=["GET"])

def delivery_detail():
    do = request.args.get("do")
    order_line = PurchaseOrderLine.query.filter_by(delivery_order_id=int(do)).all()
    
    delivery_order = DeliveryOrder.query.get(int(do))
    purchase_event = PurchaseEvent.query.get(int(delivery_order.purchase_event_id))
    po_odoo = PurchaseOrderOdoo.query.get(int(purchase_event.purchase_order_odoo_id))
    purchase_order_list = PurchaseOrder.query.filter_by(purchase_event_id=purchase_event.id)

    available_order_line = []
    for order in purchase_order_list:
        order_lines = PurchaseOrderLine.query.filter(and_(PurchaseOrderLine.delivery_order_id==None, PurchaseOrderLine.purchase_order_id == order.id))
        for order2 in order_lines:
            available_order_line.append(order2)
    
    print(available_order_line)

    return render_template('delivery/delivery_detail.html', do=do, order_line=order_line, DeliveryOrder=DeliveryOrder, ProductOdoo=ProductOdoo, delivery_order=delivery_order, purchase_event = purchase_event, available_order_line = available_order_line, po_odoo=po_odoo)

@bp.route('/detail/delete', methods=["GET"])
def delivery_detail_delete():
    order_line = request.args.get("order_line")
    print(order_line)
    order_line = PurchaseOrderLine.query.get(int(order_line))
    if order_line:
        order_line.delivery_order_id = None
        db.session.commit()
    return redirect(request.referrer)

@bp.route('/delete', methods=["GET"])
def delivery_delete():
    do = request.args.get("do")
    delivery_order = DeliveryOrder.query.get(int(do))
    db.session.delete(delivery_order)
    db.session.commit()
    return redirect(request.referrer)

@bp.route('/detail/add', methods=["GET"])
def delivery_detail_add():
    do = request.args.get('do')
    barcode = request.args.get('barcode')

    delivery_order = DeliveryOrder.query.filter_by(id=int(do)).first()
    order_line = PurchaseOrderLine.query.filter_by(barcode=barcode).first()

    if order_line :
        order_line.delivery_order_id = delivery_order.id
        db.session.commit()

    return redirect(f"/delivery/detail?do={delivery_order.id}")

@bp.route('/letter', methods=["GET","POST"])
def delivery_letter():
    do = request.args.get('do')
    delivery_order = DeliveryOrder.query.get(int(do))
    order_line = PurchaseOrderLine.query.filter_by(delivery_order_id=delivery_order.id).all()

    return render_template('delivery/delivery_letter.html', delivery_order=delivery_order, order_line=order_line)




