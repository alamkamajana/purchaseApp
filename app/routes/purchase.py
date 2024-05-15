import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

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
    purchaser_id = request.form['purchaser']
    cashier_id = request.form['cashier']
        
    
    purchase_event = PurchaseEvent(fund=fund, purchaser_id=purchaser_id, cashier_id=cashier_id)
    db.session.add(purchase_event)
    db.session.commit()

    return redirect(url_for('purchase.event_list'))

@bp.route('/event/update', methods=["POST"])
def event_update():
    # Retrieve updated data from the POST request
    updated_data = request.json
    
    # Update the data dictionary
    event = PurchaseEvent.query.filter_by(id=updated_data.get('id')).first()  # Example: Update the user with ID 1
    if event:
        event.fund = updated_data.get('fund', event.fund)
        event.purchaser_id = updated_data.get('purchaser_id', event.purchaser_id)
        event.cashier_id = updated_data.get('cashier_id', event.cashier_id)
        db.session.commit()
        return jsonify({'message': 'Data updated successfully',
                        'fund': event.fund,
                        'purchaser': event.purchaser.login,
                        'cashier': event.cashier.login
                        })
    else:
        return jsonify({'message': 'User not found'}), 404

@bp.route('/transaction', methods=["GET"])
def transaction_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Transaction.query.order_by(Transaction.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    transaction_list = pagination.items
    total_pages = pagination.pages
    po_list = PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).all()
    event_list = PurchaseEvent.query.order_by(PurchaseEvent.id.desc()).all()
    farmer_list = Farmer.query.order_by(Farmer.farmer_name.asc()).all()
    # transaction_list = Transaction.query.order_by(Transaction.id.desc()).all()
    return render_template('purchase/transaction.html', po_list=po_list, event_list=event_list, farmer_list=farmer_list, transaction_list=transaction_list, page=page, total_pages=total_pages)

@bp.route('/transaction/add', methods=["POST"])
def transaction_add():

    purchase_order_id = request.form['purchase-order']
    purchase_event_id = request.form['purchase-event']
    farmer_id = request.form['farmer']
    price_unit = request.form['price-unit']
    qty = request.form['qty']
        
    
    new_transaction = Transaction(
        purchase_order_id=purchase_order_id, 
        purchase_event_id=purchase_event_id, 
        farmer_id=farmer_id,
        price_unit=float(price_unit),
        qty=float(qty))
    db.session.add(new_transaction)
    db.session.commit()

    return redirect(url_for('purchase.transaction_list'))

@bp.route('/transaction/update', methods=["POST"])
def transaction_update():
    # Retrieve updated data from the POST request
    updated_data = request.json
    
    # Update the data dictionary
    transaction = Transaction.query.filter_by(id=updated_data.get('id')).first()  # Example: Update the user with ID 1
    if transaction:
        
        transaction.purchase_order_id = updated_data.get('purchase_order_id', transaction.purchase_order_id)
        transaction.purchase_event_id = updated_data.get('purchase_event_id', transaction.purchase_event_id)
        transaction.farmer_id = updated_data.get('farmer_id', transaction.farmer_id)
        transaction.price_unit = updated_data.get('price_unit', transaction.price_unit)
        transaction.qty = updated_data.get('qty', transaction.qty)
        transaction.subtotal = float(updated_data.get('qty', transaction.qty)) * float(updated_data.get('price_unit', transaction.price_unit))
        db.session.commit()
        return jsonify({'message': 'Data updated successfully',
                        'po': transaction.purchase_order.name,
                        'event': transaction.purchase_event.name,
                        'farmer': transaction.farmer.farmer_name,
                        'price_unit': transaction.price_unit,
                        'qty': transaction.qty,
                        'subtotal': transaction.subtotal
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
    


    