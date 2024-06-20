from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import requests
from app.models.models_odoo import ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, ResUserOdoo, \
    NfcappCommodityOdoo, NfcappCommodityItemOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.db import db
from app.models.models import User, PurchaseOrder, PurchaseOrderLine, Money, PurchaseEvent
import ast
from flask import jsonify
from sqlalchemy import and_
from datetime import datetime
import random
import string

load_dotenv()
bp = Blueprint('cashier', __name__, url_prefix='/cashier')
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')

def generate_unique_sequence_number(model, column, length=4, prefix=""):
    sequence_number = prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    if not model.query.filter(column == sequence_number).first():
        return sequence_number
@bp.route('/index', methods=["GET"])
def cashier_index():
    pe = request.args.get("pe")
    purchase_orders = PurchaseOrder.query.filter(
        and_(
            PurchaseOrder.purchase_event_id == int(pe),
            PurchaseOrder.status.ilike('confirm')
        )
    ).order_by(PurchaseOrder.id.desc())
    purchase_order_paid = [po for po in purchase_orders if po.compute_is_paid]
    purchase_order_not_paid = [po for po in purchase_orders if not po.compute_is_paid]
    purchase_event = PurchaseEvent.query.get(int(pe))
    purchase_order = PurchaseOrderOdoo.query.get(purchase_event.purchase_order_odoo_id)
    return render_template('cashier/cashier.html', pe=pe, purchase_event=purchase_event,
                           purchase_order_paid=purchase_order_paid, purchase_order_not_paid=purchase_order_not_paid,
                           NfcappFarmerOdoo=NfcappFarmerOdoo, purchase_order=purchase_order)


@bp.route('/search/po', methods=["GET", "POST"])
def cashier_search_po():
    if request.method.lower() == 'post':
        po = request.form['po']
    else:
        po = request.args.get('po')
    purchase_order = PurchaseOrder.query.filter_by(name=po).first()
    if purchase_order:
        return jsonify({'po': purchase_order.id if purchase_order else None})


@bp.route('/po/detail', methods=["GET"])
def cashier_po_detail():
    try:
        po = request.args.get('po')

        purchase_order = PurchaseOrder.query.filter_by(id=int(po)).first()
        purchase_event = PurchaseEvent.query.get(purchase_order.purchase_event_id)
        farmer = NfcappFarmerOdoo.query.filter_by(id=purchase_order.farmer_id).first()
        odoo_purchase_order = PurchaseOrderOdoo.query.get(purchase_event.purchase_order_odoo_id)
        order_line = PurchaseOrderLine.query.filter_by(purchase_order_id=purchase_order.id).all()
        money_data = Money.query.filter_by(purchase_order_id=purchase_order.id).order_by(Money.id.desc()).all()
        payment_debt = purchase_order.amount_total
        money_total = sum(money.amount for money in money_data)
        payment_debt += money_total
        paid_total = -money_total

        return render_template('cashier/po_details.html', farmer=farmer, purchase_order=purchase_order,
                               NfcappFarmerOdoo=NfcappFarmerOdoo, paid_total = paid_total, payment_debt=payment_debt, order_line=order_line,
                               ProductOdoo=ProductOdoo, money_data=money_data, PurchaseOrder=PurchaseOrder,
                               purchase_event=purchase_event, odoo_purchase_order=odoo_purchase_order)
    except Exception as e:
        print(e)


@bp.route('/payment/add', methods=["GET"])
def cashier_payment_add():
    try:
        po = request.args.get('po')
        purchase_order = PurchaseOrder.query.filter_by(id=int(po)).first()
        return redirect(request.referrer)
    except Exception as e:
        print(e)


@bp.route('/money/add2', methods=["GET"])
def cashier_money_add2():
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
        money = Money(amount=amount,note=note,purchase_event_id=purchase_event_id,number=money_name,purchase_order_id=purchase_order_id if purchase_order_id else None, created = today_datetime)
        print(money)
        db.session.add(money)
        db.session.commit()
        return redirect(request.referrer)
    except Exception as e :
        print(e)

@bp.route('/money/add', methods=["GET"])
def cashier_money_add():
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
        money = Money(amount=amount,note=note,purchase_event_id=purchase_event_id,number=money_name,purchase_order_id=purchase_order_id if purchase_order_id else None, created = today_datetime)
        print(money)
        db.session.add(money)
        db.session.commit()
        return redirect(request.referrer)
    except Exception as e :
        print(e)
