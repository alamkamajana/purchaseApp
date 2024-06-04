import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlalchemy import and_, create_engine, or_

from flask import jsonify, send_file
from app.models.db import db
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.models_odoo import ResUserOdoo, ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, NfcappCommodityItemOdoo, NfcappCommodityOdoo, NfcappClusterOdoo, NfcappStationOdoo
from app.models.models import PurchaseEvent,User, PurchaseOrder, PurchaseOrderLine

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
import io
import base64


bp = Blueprint('purchase', __name__, url_prefix='/purchase')

def generate_unique_sequence_number(model, column, length=8, prefix=""):
    sequence_number = prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    if not model.query.filter(column == sequence_number).first():
        return sequence_number

def get_current_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


@bp.route('/search_farmers', methods=["POST","GET"])
def transaction_search_farmer():
    search_term = request.args.get('q')
    if not search_term:
        return jsonify(farmers=[])  # Return empty list if no search term is provided

    farmers = NfcappFarmerOdoo.query.filter(NfcappFarmerOdoo.farmer_name.ilike(f'%{search_term}%')).all()
    farmer_data = [{'farmer_name': farmer.farmer_name} for farmer in farmers]
    return jsonify(farmers=farmer_data)

@bp.route('/search/farmer', methods=["GET"])
@login_required
def purchase_search_farmer_bycode():
    query = request.args.get('q', 0)
    group_id = request.args.get('farmer_group', 0, type=int)
    station_id = request.args.get('farmer_station', 0, type=int)
    pe = request.args.get('pe', 1, type=int)
    stations = NfcappStationOdoo.query.all()
    farmer_groups = NfcappClusterOdoo.query.all()
    if query or group_id or station_id:
        if group_id :
            farmers = NfcappFarmerOdoo.query.filter(NfcappFarmerOdoo.parent_id==group_id).filter(or_(NfcappFarmerOdoo.farmer_name.ilike(f'%{query}%'),NfcappFarmerOdoo.code.ilike(f'%{query}%'))).all()
        elif station_id:
            farmers = NfcappFarmerOdoo.query.filter(NfcappFarmerOdoo.station_id==station_id).filter(or_(NfcappFarmerOdoo.farmer_name.ilike(f'%{query}%'),NfcappFarmerOdoo.code.ilike(f'%{query}%'))).all()
        else:
            farmers = NfcappFarmerOdoo.query.filter(or_(NfcappFarmerOdoo.farmer_name.ilike(f'%{query}%'),NfcappFarmerOdoo.code.ilike(f'%{query}%'))).all()
        return render_template('purchase/search_farmer.html', pe=pe, farmers = farmers, tab=2, name = query, farmer_groups=farmer_groups, stations=stations, selected_group=group_id, selected_station=station_id)
    # transaction_list = Transaction.query.order_by(Transaction.id.desc()).all()
    return render_template('purchase/search_farmer.html', pe=pe, farmer_groups=farmer_groups, stations=stations)

@bp.route('/farmer/detail', methods=["GET"])
@login_required
def purchase_farmer_detail():
    pe = request.args.get('pe', 1, type=int)
    farmer_code = request.args.get('farmer_code')
    farmer = NfcappFarmerOdoo.query.filter_by(code=farmer_code).first()
    commodity_items = NfcappCommodityItemOdoo.query.filter(
            NfcappCommodityItemOdoo.farmer_id == farmer.odoo_id,
            NfcappCommodityItemOdoo.product_id.isnot(None)
    ).all()

    # transaction_list = Transaction.query.order_by(Transaction.id.desc()).all()
    return render_template('purchase/farmer_detail.html', pe=pe, farmer=farmer, commodity_items=commodity_items)


@bp.route('/order', methods=["GET"])
@login_required
def transaction_order():
    purchase_orders = request.args.get('po', 0, type=int)
    po = PurchaseOrder.query.filter_by(id=purchase_orders).first()
    event = PurchaseEvent.query.filter_by(id=po.purchase_event_id).first()
    farmer = NfcappFarmerOdoo.query.filter_by(id=po.farmer_id).first()

    pagination = PurchaseOrderLine.query.filter_by(purchase_order_id=po.id).order_by(
        PurchaseOrderLine.id.desc())
    transaction_list = pagination
    po_lines = PurchaseOrderLine.query.filter_by(purchase_order_id=po.id).all()
    total_price = 0
    product_list = ProductOdoo.query.all()

    purchase_order_odoo = PurchaseOrderOdoo.query.filter_by(id=event.purchase_order_odoo_id).first().odoo_id
    purchase_order_line_odoo = PurchaseOrderLineOdoo.query.filter_by(order_id=purchase_order_odoo).all()
    po_line_product_arr = []
    for product in purchase_order_line_odoo :
        po_line_product_arr.append(product.product_id)

    farmer_itemcodelist = NfcappCommodityItemOdoo.query.filter_by(farmer_id=farmer.odoo_id).all()

    item_odoo_arr = []
    for i in farmer_itemcodelist :
        if i.odoo_id not in item_odoo_arr :
            item_odoo_arr.append(i.odoo_id)
    # print(farmer.id)
    # print(NfcappCommodityItemOdoo.query.filter_by(farmer_id=farmer.odoo_id).all())
    commodity_item_product_arr = []
    for item in item_odoo_arr :
        commodityitem = NfcappCommodityItemOdoo.query.filter_by(odoo_id=int(item)).first()
        if commodityitem.product_id :
            # commodity_item_product_arr.append(commodityitem.product_id)
            commodityitem_json = {}
            commodityitem_json['commodityitem_id'] = commodityitem.id
            commodityitem_json['commodityitem_name'] = commodityitem.code
            commodityitem_json['commodityitem_price'] = commodityitem.price
            commodityitem_json['product_id'] = commodityitem.product_id
            commodityitem_json['product_name'] = commodityitem.product_name
            commodityitem_json['commodity_id'] = commodityitem.commodity_id
            commodityitem_json['certStatus'] = commodityitem.certStatus
            commodity_item_product_arr.append(commodityitem_json)


    product_can_purchase_arr= []
    for commodity_data in commodity_item_product_arr:
        if commodity_data['product_id'] in po_line_product_arr:
            product_can_purchase_arr.append(commodity_data)
    product_ids = [p['product_id']for p in commodity_item_product_arr]
    products_list = ProductOdoo.query.filter(ProductOdoo.odoo_id.in_(product_ids)).all()
    products_list_arr = []

    for po_line in po_lines:
        total_price += po_line.subtotal

    po_status = po.status if po else None
    # print(po_line_product_arr)
    # print(commodity_item_product_arr)
    farmer_odoo = NfcappFarmerOdoo.query.filter_by(odoo_id=farmer.odoo_id).first()

    po_json = {}
    po_order_line = PurchaseOrderLineOdoo.query.filter_by(order_id=int(event.purchase_order_odoo.odoo_id)).all()
    grand_total=0
    for order in po_order_line:
        grand_total=grand_total+(order.price_unit*order.product_qty)

    commodity_items = NfcappCommodityItemOdoo.query.filter(
            NfcappCommodityItemOdoo.farmer_id == farmer.odoo_id,
            NfcappCommodityItemOdoo.product_id.isnot(None)
    ).all()

    return render_template('purchase/transaction.html', po=po, event=event, farmer=farmer,farmer_odoo=farmer_odoo,
                           product_list=product_can_purchase_arr, transaction_list=transaction_list, total_price=total_price,
                           ProductOdoo=ProductOdoo, po_status = po_status, commodity_item_product_arr=commodity_item_product_arr,
                           po_line_product_arr=po_line_product_arr, commodity_items=commodity_items,
                           po_order_line=po_order_line, grand_total=grand_total )

@bp.route('/payment-note', methods=["GET"])
@login_required
def purchase_payment_note():
    po = request.args.get('po', 1, type=int)
    order = PurchaseOrder.query.get(po)

    # transaction_list = Transaction.query.order_by(Transaction.id.desc()).all()
    return render_template('purchase/payment_note.html', purchase_order=order)

@bp.route('/order/add', methods=["POST","GET"])
@login_required
def transaction_order_add():
    if request.method.lower() == 'post' :
        purchase_event = request.form['pe']
        farmer = request.form['farmer']
    else :
        purchase_event = request.args.get('pe')
        farmer = request.args.get('farmer')
    po_name = generate_unique_sequence_number(PurchaseOrder, PurchaseOrder.name, prefix="ORDER-")
    new_po = PurchaseOrder(name=po_name,purchase_event_id=int(purchase_event), farmer_id=int(farmer), status='draft')
    db.session.add(new_po)
    db.session.commit()
    url = f"/purchase/order?po={new_po.id}&farmer={farmer}"
    return redirect(url)


@bp.route('/order/add-signature', methods=["GET","POST"])
@login_required
def transaction_add_signature():
    po = request.form['po']
    signature = request.form['signature']
    purchase_order = PurchaseOrder.query.get(int(po))
    siganture_binary = None
    if signature:
        signature_data = signature.split(',', 1)[1]
        siganture_binary = signature_data
        purchase_order.signature = base64.b64decode(siganture_binary)
        db.session.commit()

    return {"status" : 200, "message" : "success"}

@bp.route('/order/get-signature')
@login_required
def order_get_signature():
    po = request.args.get("po")
    purchase_order = PurchaseOrder.query.get(int(po))
    if purchase_order.signature:
        return send_file(io.BytesIO(purchase_order.signature), mimetype='image/png')
    else:
        return jsonify({"error": "Signature not found"}), 404


@bp.route('/transaction', methods=["GET"])
@login_required
def transaction_list():
    try :
        event_id = request.args.get('pe', 0, type=int)
        purchase_lists = PurchaseOrder.query.filter_by(purchase_event_id=event_id).order_by(PurchaseOrder.id.desc()).all()
        event_obj = PurchaseEvent.query.filter_by(id=event_id).first()
        po_json = {}
        po_order_line = PurchaseOrderLineOdoo.query.filter_by(order_id=int(event_obj.purchase_order_odoo.odoo_id)).all()
        grand_total=0
        for order in po_order_line:
            grand_total=grand_total+(order.price_unit*order.product_qty)
        price_list = []
        for purchase in purchase_lists:
            total_price = 0
            po_lines = PurchaseOrderLine.query.filter_by(purchase_order_id=purchase.id).all()
            for po_line in po_lines:
                total_price = total_price + po_line.subtotal
            price_data_json = {}
            price_data_json['po_id'] = purchase.id
            price_data_json['total'] = total_price
            price_list.append(price_data_json)


        return render_template('purchase/purchase.html', purchase_event=event_obj, purchase_lists=purchase_lists, Farmer=NfcappFarmerOdoo, price_list=price_list, po_order_line=po_order_line, grand_total=grand_total)

    except Exception as e :
        print(e)

@bp.route('/transaction/add', methods=["POST","GET"])
@login_required
def transaction_add():
    purchase_order_id = request.form['po']
    purchase_event_id = request.form['pe']
    farmer_id = request.form['farmer_id']

    product = request.form['product']
    price_unit = request.form['price-unit']
    qty = request.form['qty']
    barcode = request.form['barcode']
    note = request.form['note']
    subtotal = request.form['subtotal']
    product_odoo = ProductOdoo.query.filter_by(odoo_id=int(product)).first()


    new_transaction = PurchaseOrderLine(
        purchase_order_id=purchase_order_id,
        unit_price = price_unit,
        qty = qty,
        barcode = barcode,
        note=note,
        subtotal = subtotal,
        product_odoo_id=product_odoo.id
    )

    db.session.add(new_transaction)
    db.session.commit()
    url = "/purchase/order?purchase-event=" + purchase_event_id + "&po=" + purchase_order_id + "&farmer=" + farmer_id
    return redirect(url)

@bp.route('/transaction/create', methods=["POST","GET"])
@login_required
def transaction_create():
    purchase_event_id = request.args.get("purchase-event")
    purchase_order_id = request.args.get("purchase-order")
    farmer_id = request.args.get("farmer_id")

    event = PurchaseEvent.query.filter_by(id=int(purchase_event_id)).first()
    farmer = NfcappFarmerOdoo.query.filter_by(id=int(farmer_id)).first()

    purchase_order_odoo = PurchaseOrderOdoo.query.filter_by(id=event.purchase_order_odoo_id).first().odoo_id
    purchase_order_line_odoo = PurchaseOrderLineOdoo.query.filter_by(order_id=purchase_order_odoo).all()
    po_line_product_arr = []
    for product in purchase_order_line_odoo:
        po_line_product_arr.append(product.product_id)

    farmer_itemcodelist = NfcappCommodityItemOdoo.query.filter_by(farmer_id=farmer.odoo_id).all()

    item_odoo_arr = []
    for i in farmer_itemcodelist:
        if i.odoo_id not in item_odoo_arr:
            item_odoo_arr.append(i.odoo_id)

    commodity_item_product_arr = []
    for item in item_odoo_arr:
        commodityitem = NfcappCommodityItemOdoo.query.filter_by(odoo_id=int(item)).first()
        if commodityitem.product_id:
            commodityitem_json = {}
            commodityitem_json['commodityitem_id'] = commodityitem.id
            commodityitem_json['commodityitem_name'] = commodityitem.code
            commodityitem_json['commodityitem_price'] = commodityitem.price
            commodityitem_json['product_id'] = commodityitem.product_id
            commodityitem_json['product_id_code'] = commodityitem.product_id_code
            commodityitem_json['product_name'] = commodityitem.product_name
            commodityitem_json['commodity_id'] = commodityitem.commodity_id
            commodityitem_json['commodity_name'] = commodityitem.commodity_name
            commodityitem_json['variant'] = commodityitem.variant
            commodityitem_json['certStatus'] = commodityitem.certStatus
            commodity_item_product_arr.append(commodityitem_json)

    product_can_purchase_arr = []
    for commodity_data in commodity_item_product_arr:
        if commodity_data['product_id'] in po_line_product_arr:
            product_can_purchase_arr.append(commodity_data)

    datas = {
        "po" : purchase_order_id,
        "pe" : purchase_event_id,
        "farmer_id" : farmer_id
    }

    return render_template('purchase/transaction_create.html',product_can_purchase=product_can_purchase_arr, datas=datas)



@bp.route('/transaction/delete', methods=["POST","GET"])
@login_required
def transaction_delete():
    transaction = request.args.get("transaction")
    purchase_order_id = request.args.get("purchase-order")
    purchase_event_id = request.args.get("purchase-event")
    farmer_id = request.args.get("farmer_id")
    po_line = PurchaseOrderLine.query.get(int(transaction))
    db.session.delete((po_line))
    db.session.commit()
    url = "/purchase/order?purchase-event=" + purchase_event_id + "&po=" + purchase_order_id + "&farmer=" + farmer_id
    return redirect(url)


@bp.route('/transaction/update', methods=["POST"])
@login_required
def transaction_update():
    transaction_id = request.form['transaction']
    product = request.form['product']
    price_unit = request.form['price-unit']
    qty = request.form['qty']
    barcode = request.form['barcode']
    note = request.form['note']
    product_odoo = ProductOdoo.query.filter_by(odoo_id=int(product)).first()


    # Update the data dictionary
    transaction = PurchaseOrderLine.query.filter_by(id=transaction_id).first()
    po = PurchaseOrder.query.get(transaction.purchase_order_id)
    if transaction:

        transaction.unit_price = price_unit
        transaction.qty = qty
        transaction.product_odoo_id = product_odoo.id
        transaction.barcode = barcode
        transaction.note = note

        transaction.subtotal = float(qty) * float(price_unit)
        db.session.commit()
        return redirect(f"/purchase/order?purchase-event={po.purchase_event_id}&po={po.id}&farmer={po.farmer_id}")
    else:
        return jsonify({'message': 'Transaction not found'}), 404


@bp.route('/transaction/detail', methods=["POST","GET"])
@login_required
def transaction_detail():
    transaction = request.args.get("transaction")
    purchase_event_id = request.args.get("purchase-event")
    farmer_id = request.args.get("farmer_id")
    order_line = PurchaseOrderLine.query.get(int(transaction))

    event = PurchaseEvent.query.filter_by(id=int(purchase_event_id)).first()
    farmer = NfcappFarmerOdoo.query.filter_by(id=int(farmer_id)).first()

    purchase_order_odoo = PurchaseOrderOdoo.query.filter_by(id=event.purchase_order_odoo_id).first().odoo_id
    purchase_order_line_odoo = PurchaseOrderLineOdoo.query.filter_by(order_id=purchase_order_odoo).all()
    po_line_product_arr = []
    for product in purchase_order_line_odoo:
        po_line_product_arr.append(product.product_id)

    farmer_itemcodelist = NfcappCommodityItemOdoo.query.filter_by(farmer_id=farmer.odoo_id).all()

    item_odoo_arr = []
    for i in farmer_itemcodelist:
        if i.odoo_id not in item_odoo_arr:
            item_odoo_arr.append(i.odoo_id)

    commodity_item_product_arr = []
    for item in item_odoo_arr:
        commodityitem = NfcappCommodityItemOdoo.query.filter_by(odoo_id=int(item)).first()
        if commodityitem.product_id:
            commodityitem_json = {}
            commodityitem_json['commodityitem_id'] = commodityitem.id
            commodityitem_json['commodityitem_name'] = commodityitem.code
            commodityitem_json['commodityitem_price'] = commodityitem.price
            commodityitem_json['product_id'] = commodityitem.product_id
            commodityitem_json['product_name'] = commodityitem.product_name
            commodityitem_json['product_id_code'] = commodityitem.product_id_code
            commodityitem_json['commodity_id'] = commodityitem.commodity_id
            commodityitem_json['certStatus'] = commodityitem.certStatus
            commodity_item_product_arr.append(commodityitem_json)

    product_can_purchase_arr = []
    for commodity_data in commodity_item_product_arr:
        if commodity_data['product_id'] in po_line_product_arr:
            product_can_purchase_arr.append(commodity_data)
    return render_template('purchase/transaction_detail.html', purchase_order_line=order_line, product_can_purchase = product_can_purchase_arr, ProductOdoo=ProductOdoo, farmer_id=farmer_id)


@bp.route('/transaction/confirm', methods=["POST","GET"])
@login_required
def transaction_confirm():
    purchase_order = request.args.get('purchase_order')
    po = PurchaseOrder.query.filter_by(id=int(purchase_order)).first()
    po.status = 'confirm'
    db.session.commit()
    return redirect(request.referrer)

@bp.route('/transaction/confirm2', methods=["POST","GET"])
@login_required
def transaction_confirm2():
    purchase_order = request.args.get('purchase_order')
    po = PurchaseOrder.query.filter_by(id=int(purchase_order)).first()
    po.status = 'confirm'
    db.session.commit()
    return {"status" : 200, "message" : True}

@bp.route('/transaction/items', methods=["POST","GET"])
@login_required
def transaction_items():
    purchase_order = request.args.get('purchase_order')
    po = PurchaseOrder.query.filter_by(id=int(purchase_order)).first()
    data_arr = []
    for line in po.purchase_order_lines :
        product_name = ProductOdoo.query.get(line.product_odoo_id)
        commodity_item = NfcappCommodityItemOdoo.query.filter_by(product_id=product_name.odoo_id).first()
        data_json = {}
        data_json['product_code'] = commodity_item.code
        data_json['product_name'] = commodity_item.desc
        data_json['price'] = line.unit_price
        data_json['quantity'] = line.qty
        data_json['subtotal'] = line.subtotal
        data_arr.append(data_json)

    return data_arr

