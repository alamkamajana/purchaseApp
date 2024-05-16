import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlalchemy import and_, create_engine

from flask import jsonify
from app.models.db import db
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.models_odoo import ResUserOdoo, ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo
from app.models.models import PurchaseEvent, Transaction, User, Product, PurchaseOrder, PurchaseOrderLine, Farmer

bp = Blueprint('purchase', __name__, url_prefix='/purchase')

@bp.route('/report', methods=["GET"])
def purchase_report():
    return render_template('purchase/report.html')

@bp.route('/list', methods=["GET"])
def purchase_list():
    return render_template('purchase/list.html')

@bp.route('/farmer-list', methods=["GET"])
def farmer_list():
    farmers = Farmer.query.all()
    return render_template('purchase/farmer_list.html', farmers=farmers)

@bp.route('/event', methods=["GET"])
def event_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = PurchaseEvent.query.order_by(PurchaseEvent.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    events = pagination.items
    total_pages = pagination.pages
    users = User.query.all()
    # events = PurchaseEvent.query.order_by(PurchaseEvent.id).all()
    return render_template('purchase/event.html', events=events, users=users, page=page, total_pages=total_pages)

@bp.route('/event/add', methods=["POST"])
def event_add():

    fund = request.form['fund']
    ics = request.form['ics']
    ap_name = request.form['ap-name']
    purchaser_id = request.form['purchaser']
    cashier_id = request.form['cashier']
    purchase_order_odoo_id = request.form['purchase-order']
    
    purchase_event = PurchaseEvent(fund=fund, ics=ics, purchaser_id=purchaser_id, cashier_id=cashier_id, purchase_order_odoo_id=purchase_order_odoo_id, ap_name=ap_name)
    db.session.add(purchase_event)
    db.session.commit()

    return redirect(url_for('routes.purchase.event_list'))

@bp.route('/event/update', methods=["POST"])
def event_update():
    # Retrieve updated data from the POST request
    updated_data = request.json
    
    # Update the data dictionary
    event = PurchaseEvent.query.filter_by(id=updated_data.get('id')).first()  # Example: Update the user with ID 1
    if event:
        event.fund = updated_data.get('fund', event.fund)
        event.ics = updated_data.get('ics', event.ics)
        event.ap_name = updated_data.get('ap_name', event.ap_name)
        event.purchase_order_odoo_id = updated_data.get('po_id', event.purchase_order_odoo_id)
        event.purchaser_id = updated_data.get('purchaser_id', event.purchaser_id)
        event.cashier_id = updated_data.get('cashier_id', event.cashier_id)
        db.session.commit()
        return jsonify({'message': 'Data updated successfully',
                        'fund': event.fund,
                        'ics': event.ics,
                        'ap_name': event.ap_name,
                        'po': event.purchase_order_odoo.name,
                        'purchaser': event.purchaser.name,
                        'cashier': event.cashier.name
                        })
    else:
        return jsonify({'message': 'User not found'}), 404


@bp.route('/transaction', methods=["GET"])
def transaction_list():
    event_id = request.args.get('purchase-event', 0, type=int)
    farmer_id = request.args.get('farmer', 0, type=int)
    if event_id and farmer_id:
        event = PurchaseEvent.query.filter_by(id=event_id).first()
        farmer = Farmer.query.filter_by(id=farmer_id).first()
        page = request.args.get('page', 1, type=int)

        per_page = 10
        po = PurchaseOrder.query.filter(
                    and_(
                        PurchaseOrder.purchase_event_id == event_id,
                        PurchaseOrder.farmer_id == farmer_id
                    )
                ).first()

        if not po:
            po = PurchaseOrder(
                purchase_event_id=event_id,
                farmer_id=farmer_id,
                status="Draft",
            )
            db.session.add(po)
            db.session.commit()

        pagination = PurchaseOrderLine.query.filter_by(purchase_order_id=po.id).order_by(PurchaseOrderLine.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        transaction_list = pagination.items
        total_pages = pagination.pages
        po_lines = PurchaseOrderLine.query.filter_by(purchase_order_id=po.id).all()
        total_price = 0
        for po_line in po_lines:
            total_price += po_line.subtotal


        return render_template('purchase/transaction.html', po=po, event=event, farmer=farmer, transaction_list=transaction_list, page=page, total_pages=total_pages, total_price=total_price)
    else:
        return render_template('purchase/transaction_select.html')


@bp.route('/transaction/add', methods=["POST"])
def transaction_add():
    print(request.form)

    purchase_order_id = request.form['purchase-order']
    purchase_event_id = request.form['purchase-event']
    farmer_id = request.form['farmer']
    product_id = request.form['product']
    price_unit = request.form['price-unit']
    qty = request.form['qty']

    new_transaction = PurchaseOrderLine(
        purchase_order_id=purchase_order_id,

        product_odoo_id=product_id,
        unit_price=float(price_unit),
        qty=float(qty),
        subtotal=float(price_unit)*float(qty)
    )
    db.session.add(new_transaction)
    db.session.commit()

    url = "/purchase/transaction?purchase-event="+purchase_event_id+"&purchase-order="+purchase_order_id+"&farmer="+farmer_id

    return redirect(url)

@bp.route('/transaction/update', methods=["POST"])
def transaction_update():
    # Retrieve updated data from the POST request
    updated_data = request.json
    
    # Update the data dictionary
    transaction = PurchaseOrderLine.query.filter_by(id=updated_data.get('id')).first()  # Example: Update the user with ID 1
    if transaction:
        
        transaction.unit_price = updated_data.get('price_unit', transaction.unit_price)
        transaction.qty = updated_data.get('qty', transaction.qty)
        transaction.subtotal = float(updated_data.get('qty', transaction.qty)) * float(updated_data.get('price_unit', transaction.unit_price))
        db.session.commit()
        po_id = transaction.purchase_order_id
        po_lines = PurchaseOrderLine.query.filter_by(purchase_order_id=po_id).all()
        total_price = 0
        for po_line in po_lines:
            total_price += po_line.subtotal
        return jsonify({'message': 'Data updated successfully',
                        'price_unit': transaction.unit_price,
                        'qty': transaction.qty,
                        'subtotal': transaction.subtotal,
                        'total_price': total_price
                        })
    else:
        return jsonify({'message': 'Transaction not found'}), 404

@bp.route('/receipt', methods=["GET"])
def receipt_form():
    po_id = request.args.get('po', 1, type=int)
    purchase_order = PurchaseOrder.query.get(po_id)
    transaction_list = Transaction.query.filter_by(purchase_order_id=po_id).all()
    # transaction_list = Transaction.query.order_by(Transaction.id.desc()).all()
    return render_template('purchase/receipt_form.html', purchase_order = purchase_order, transaction_list = transaction_list)

@bp.route('/cashier', methods=["GET"])
def cashier_form():
    po_id = request.args.get('po', 1, type=int)
    purchase_order = PurchaseOrder.query.get(po_id)
    transaction_list = Transaction.query.filter_by(purchase_order_id=po_id).all()
    total_payment = 0.00
    for transaction in transaction_list:
        total_payment+=transaction.subtotal
    
    status = "Not Paid"

    # transaction_list = Transaction.query.order_by(Transaction.id.desc()).all()
    return render_template('purchase/cashier_form.html', purchase_order = purchase_order, transaction_list = transaction_list, total_payment= total_payment, status=status)
    


    