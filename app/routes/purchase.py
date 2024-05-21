import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlalchemy import and_, create_engine

from flask import jsonify
from app.models.db import db
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.models_odoo import ResUserOdoo, ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, NfcappCommodityItemOdoo, NfcappCommodityOdoo
from app.models.models import PurchaseEvent, Transaction, User, Product, PurchaseOrder, PurchaseOrderLine, Farmer

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


bp = Blueprint('purchase', __name__, url_prefix='/purchase')

def generate_unique_sequence_number(model, column, length=8, prefix=""):
    sequence_number = prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    if not model.query.filter(column == sequence_number).first():
        return sequence_number

def get_current_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

@bp.route("/")
@login_required
def index():
    return render_template('main_menu.html')


@bp.route('/report', methods=["GET"])
@login_required
def purchase_report():
    return render_template('purchase/report.html')


@bp.route('/list', methods=["GET"])
@login_required
def purchase_list():
    return render_template('purchase/list.html')


@bp.route('/farmer-list', methods=["GET"])
@login_required
def farmer_list():
    farmers = Farmer.query.all()
    return render_template('purchase/farmer_list.html', farmers=farmers)


@bp.route('/event', methods=["GET"])
@login_required
def event_list():
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
    return render_template('purchase/event.html', events=events, users=users, page=page, total_pages=total_pages,
                           po_list=purchase_orders, user_list=user_list, device_name=device_name, base_url=base_url)


@bp.route('/event/add', methods=["POST"])
@login_required
def event_add():
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

    return redirect(url_for('routes.purchase.event_list'))


@bp.route('/event/update', methods=["POST"])
@login_required
def event_update():
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


# @bp.route('/transaction', methods=["GET"])
# @login_required
# def transaction_list():
#
#     event_id = request.args.get('purchase-event', 0, type=int)
#     farmer_id = request.args.get('farmer', 0, type=int)
#     if event_id and farmer_id:
#         event = PurchaseEvent.query.filter_by(id=event_id).first()
#         farmer = Farmer.query.filter_by(id=farmer_id).first()
#         page = request.args.get('page', 1, type=int)
#
#         per_page = 10
#         po = PurchaseOrder.query.filter(
#             and_(
#                 PurchaseOrder.purchase_event_id == event_id,
#                 PurchaseOrder.farmer_id == farmer_id
#             )
#         ).first()
#
#         if not po:
#             po = PurchaseOrder(
#                 purchase_event_id=event_id,
#                 farmer_id=farmer_id,
#                 status="Draft",
#             )
#             db.session.add(po)
#             db.session.commit()
#
#         pagination = PurchaseOrderLine.query.filter_by(purchase_order_id=po.id).order_by(
#             PurchaseOrderLine.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
#         transaction_list = pagination.items
#         total_pages = pagination.pages
#         po_lines = PurchaseOrderLine.query.filter_by(purchase_order_id=po.id).all()
#         total_price = 0
#         product_list = ProductOdoo.query.all()
#
#
#         purchase_order_odoo = PurchaseOrderOdoo.query.filter_by(id=event.purchase_order_odoo_id).first().odoo_id
#         purchase_order_line_odoo = PurchaseOrderLineOdoo.query.filter_by(order_id=purchase_order_odoo).all()
#         po_line_product_arr = []
#         for product in purchase_order_line_odoo :
#             po_line_product_arr.append(product.product_id)
#
#         farmer_itemcodelist = list(ast.literal_eval(farmer.item_code_list)) if farmer.item_code_list else None
#         commodity_item_product_arr = []
#         for item in farmer_itemcodelist :
#             commodityitem = NfcappCommodityItemOdoo.query.filter_by(odoo_id=int(item)).first()
#             if commodityitem.product_id :
#                 # commodity_item_product_arr.append(commodityitem.product_id)
#                 commodityitem_json = {}
#                 commodityitem_json['commodityitem_id'] = commodityitem.id
#                 commodityitem_json['commodityitem_name'] = commodityitem.code
#                 commodityitem_json['commodityitem_price'] = commodityitem.price
#                 commodityitem_json['product_id'] = commodityitem.product_id
#                 commodityitem_json['product_name'] = commodityitem.product_name
#                 commodityitem_json['commodity_id'] = commodityitem.commodity_id
#                 commodity_item_product_arr.append(commodityitem_json)
#
#
#         product_can_purchase_arr= []
#         for commodity_data in commodity_item_product_arr:
#             if commodity_data['product_id'] in po_line_product_arr:
#                 product_can_purchase_arr.append(commodity_data)
#         product_ids = [p['product_id']for p in commodity_item_product_arr]
#         products_list = ProductOdoo.query.filter(ProductOdoo.odoo_id.in_(product_ids)).all()
#         products_list_arr = []
#
#         for po_line in po_lines:
#             total_price += po_line.subtotal
#
#         po_status = po.status if po else None
#         return render_template('purchase/transaction.html', po=po, event=event, farmer=farmer,
#                                product_list=product_can_purchase_arr, transaction_list=transaction_list, page=page,
#                                total_pages=total_pages, total_price=total_price, ProductOdoo=ProductOdoo, po_status = po_status)
#     else:
#         event_list = PurchaseEvent.query.all()
#         farmer_list = Farmer.query.all()
#         return render_template('purchase/transaction_select.html', event_list=event_list, farmer_list=farmer_list)


@bp.route('/order', methods=["GET"])
@login_required
def transaction_order():
    purchase_orders = request.args.get('po', 0, type=int)
    po = PurchaseOrder.query.filter_by(id=purchase_orders).first()
    event = PurchaseEvent.query.filter_by(id=po.purchase_event_id).first()
    farmer = Farmer.query.filter_by(id=po.farmer_id).first()

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
    return render_template('purchase/transaction.html', po=po, event=event, farmer=farmer,farmer_odoo=farmer_odoo,
                           product_list=product_can_purchase_arr, transaction_list=transaction_list, total_price=total_price, ProductOdoo=ProductOdoo, po_status = po_status, commodity_item_product_arr=commodity_item_product_arr,po_line_product_arr=po_line_product_arr)


@bp.route('/order/add', methods=["POST","GET"])
@login_required
def transaction_order_add():
    if request.method.lower() == 'post' :
        purchase_event = request.form['pe']
        farmer = request.form['farmer']
    else :
        purchase_event = request.args.get('pe')
        farmer = request.args.get('farmer')
    po_name = generate_unique_sequence_number(PurchaseOrder, PurchaseOrder.name, prefix="")
    new_po = PurchaseOrder(
        name=po_name,purchase_event_id=int(purchase_event), farmer_id=int(farmer), status='draft'
    )
    db.session.add(new_po)
    db.session.commit()
    # farmer_id = request.form['farmer']
    # product_id = request.form['product']
    # price_unit = request.form['price-unit']
    # qty = request.form['qty']
    # product_odoo = ProductOdoo.query.filter_by(odoo_id=int(product_id)).first()
    # new_transaction = PurchaseOrderLine(
    #     purchase_order_id=purchase_order_id,
    #
    #     product_odoo_id=product_odoo.id,
    #     unit_price=float(price_unit),
    #     qty=float(qty),
    #     subtotal=float(price_unit) * float(qty)
    # )
    # db.session.add(new_transaction)
    # db.session.commit()
    #
    url = f"/purchase/order?po={new_po.id}&farmer={farmer}"
    return redirect(url)

@bp.route('/search_farmers', methods=["POST","GET"])
def transaction_search_farmer():
    search_term = request.args.get('q')
    if not search_term:
        return jsonify(farmers=[])  # Return empty list if no search term is provided

    farmers = Farmer.query.filter(Farmer.farmer_name.ilike(f'%{search_term}%')).all()
    farmer_data = [{'farmer_name': farmer.farmer_name} for farmer in farmers]
    return jsonify(farmers=farmer_data)


@bp.route('/transaction', methods=["GET"])
@login_required
def transaction_list():
    try :
        event_id = request.args.get('pe', 0, type=int)
        purchase_lists = PurchaseOrder.query.filter_by(purchase_event_id=event_id).all()
        event_obj = PurchaseEvent.query.filter_by(id=event_id).first()
        return render_template('purchase/transaction_po.html', purchase_event=event_obj, purchase_lists=purchase_lists, Farmer=Farmer)

    except Exception as e :
        print(e)


@bp.route('/transaction/add', methods=["POST"])
@login_required
def transaction_add():


    purchase_order_id = request.form['purchase-order']
    purchase_event_id = request.form['purchase-event']
    farmer_id = request.form['farmer']
    product_id = request.form['product']
    price_unit = request.form['price-unit']
    barcode = request.form['barcode']
    qty = request.form['qty']
    product_odoo = ProductOdoo.query.filter_by(odoo_id=int(product_id)).first()
    new_transaction = PurchaseOrderLine(
        purchase_order_id=purchase_order_id,

        product_odoo_id=product_odoo.id,
        unit_price=float(price_unit),
        qty=float(qty),
        subtotal=float(price_unit) * float(qty),
        barcode=barcode
    )
    db.session.add(new_transaction)
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
    product_odoo = ProductOdoo.query.filter_by(odoo_id=int(product)).first()


    # Update the data dictionary
    transaction = PurchaseOrderLine.query.filter_by(id=transaction_id).first()  # Example: Update the user with ID 1
    if transaction:

        transaction.unit_price = price_unit
        transaction.qty = qty
        transaction.product_odoo_id = product_odoo.id
        transaction.subtotal = float(qty) * float(price_unit)
        db.session.commit()
        return redirect(request.referrer)
    else:
        return jsonify({'message': 'Transaction not found'}), 404


@bp.route('/transaction/confirm', methods=["POST"])
@login_required
def transaction_confirm():
    purchase_order = request.form['purchase_order']
    po = PurchaseOrder.query.filter_by(id=int(purchase_order)).first()
    po.status = 'confirm'
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Purchase order confirmed!'})




@bp.route('/receipt', methods=["GET"])
@login_required
def receipt_form():
    po_id = request.args.get('po', 1, type=int)
    purchase_order = PurchaseOrder.query.get(po_id)
    transaction_list = Transaction.query.filter_by(purchase_order_id=po_id).all()
    # transaction_list = Transaction.query.order_by(Transaction.id.desc()).all()
    return render_template('purchase/receipt_form.html', purchase_order=purchase_order,
                           transaction_list=transaction_list)


@bp.route('/cashier', methods=["GET"])
@login_required
def cashier_form():
    po_id = request.args.get('po', 1, type=int)
    purchase_order = PurchaseOrder.query.get(po_id)
    transaction_list = Transaction.query.filter_by(purchase_order_id=po_id).all()
    total_payment = 0.00
    for transaction in transaction_list:
        total_payment += transaction.subtotal

    status = "Not Paid"

    # transaction_list = Transaction.query.order_by(Transaction.id.desc()).all()
    return render_template('purchase/cashier_form.html', purchase_order=purchase_order,
                           transaction_list=transaction_list, total_payment=total_payment, status=status)

@bp.route('/search/farmer', methods=["GET"])
@login_required
def purchase_search_farmer_bycode():
    pe = request.args.get('pe', 1, type=int)
    # transaction_list = Transaction.query.order_by(Transaction.id.desc()).all()
    return render_template('purchase/search_farmer.html', pe=pe)


@bp.route('/farmer/detail', methods=["GET"])
@login_required
def purchase_farmer_detail():
    pe = request.args.get('pe', 1, type=int)
    farmer_code = request.args.get('farmer_code')
    farmer = NfcappFarmerOdoo.query.filter_by(code=farmer_code).first()

    # transaction_list = Transaction.query.order_by(Transaction.id.desc()).all()
    return render_template('purchase/farmer_detail.html', pe=pe, farmer=farmer)



