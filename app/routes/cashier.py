from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import requests
from app.models.models_odoo import ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, ResUserOdoo, NfcappCommodityOdoo, NfcappCommodityItemOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.db import db
from app.models.models import User, PurchaseOrder, PurchaseOrderLine, Money, PurchaseEvent
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
    pe = request.args.get("pe")
    purchase_order_paid = PurchaseOrder.query.filter(
        PurchaseOrder.purchase_event_id == int(pe),
        PurchaseOrder.is_paid == True
    ).all()
    purchase_order_not_paid = PurchaseOrder.query.filter(
        PurchaseOrder.purchase_event_id == int(pe),
        PurchaseOrder.is_paid == False or PurchaseOrder.is_paid == None
    ).all()
    purchase_event = PurchaseEvent.query.get(int(pe))
    purchase_order = PurchaseOrderOdoo.query.get(purchase_event.purchase_order_odoo_id)
    return render_template('cashier/cashier.html', pe=pe,purchase_event=purchase_event, purchase_order_paid=purchase_order_paid, purchase_order_not_paid=purchase_order_not_paid, NfcappFarmerOdoo=NfcappFarmerOdoo,purchase_order=purchase_order)


@bp.route('/search/po', methods=["GET","POST"])
@login_required
def cashier_search_po():
    if request.method.lower() == 'post' :
        po = request.form['po']
    else :
        po = request.args.get('po')
    purchase_order = PurchaseOrder.query.filter_by(name=po).first()
    if purchase_order:
        return jsonify({'po': purchase_order.id if purchase_order else None})



@bp.route('/po/detail', methods=["GET"])
@login_required
def cashier_po_detail():
    try :
        po = request.args.get('po')

        purchase_order = PurchaseOrder.query.filter_by(id=int(po)).first()
        purchase_event = PurchaseEvent.query.get(purchase_order.purchase_event_id)
        farmer = NfcappFarmerOdoo.query.filter_by(id=purchase_order.farmer_id).first()
        odoo_purchase_order = PurchaseOrderOdoo.query.get(purchase_event.purchase_order_odoo_id)
        order_line = PurchaseOrderLine.query.filter_by(purchase_order_id=purchase_order.id).all()
        money_data = Money.query.filter_by(purchase_order_id=purchase_order.id).filter(Money.amount < 0).all()
        payment_debt = purchase_order.amount_total
        money_total = sum(money.amount for money in money_data)
        payment_debt += money_total

        return render_template('cashier/po_details.html',farmer=farmer, purchase_order=purchase_order, NfcappFarmerOdoo=NfcappFarmerOdoo, payment_debt=payment_debt, order_line=order_line, ProductOdoo=ProductOdoo, money_data=money_data, PurchaseOrder=PurchaseOrder,purchase_event=purchase_event,odoo_purchase_order=odoo_purchase_order)
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



