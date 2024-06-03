from flask import (
    Blueprint, redirect, render_template, request, send_file
)
from io import BytesIO
import random
import socket
import string
from datetime import datetime

from flask import (
    Blueprint, redirect, render_template, request, send_file
)

from app.models.db import db
from app.models.models import PurchaseEvent, Expense, Money

bp = Blueprint('expense', __name__, url_prefix='/expense')

def generate_unique_sequence_number(model, column, length=8, prefix=""):
    sequence_number = prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    if not model.query.filter(column == sequence_number).first():
        return sequence_number

def get_current_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


@bp.route('/index', methods=["POST","GET"])
def expense_index():
    event_id = request.args.get("pe")
    purchase_event = PurchaseEvent.query.get(int(event_id))
    expenses = Expense.query.filter_by(purchase_event_id=purchase_event.id).all()
    return render_template('expense/index.html', expense_list=expenses, purchase_event=purchase_event)

@bp.route('/create', methods=["POST","GET"])
def expense_create():
    event_id = request.args.get("pe")
    purchase_event = PurchaseEvent.query.get(int(event_id))
    return render_template('expense/create.html', purchase_event=purchase_event)

@bp.route('/delete', methods=["POST","GET"])
def expense_delete():
    expense_id = request.args.get("expense_id")
    expense = Expense.query.get(int(expense_id))
    # money = Money.query.filter_by(expense_id=expense.id).first()
    # db.session.delete(money)
    # db.session.commit()
    db.session.delete(expense)
    db.session.commit()
    return redirect(request.referrer)

@bp.route('/expense_image/<int:expense_id>')
def expense_image(expense_id):
    expense = Expense.query.get(expense_id)
    if expense and expense.image:
        return send_file(BytesIO(expense.image), mimetype='image/jpeg')
    return "", 404

@bp.route('/add', methods=["POST","GET"])
def expense_add():
    file = request.files['image']
    purchase_event_id = request.form['purchase_event_id']
    amount = request.form['amount']
    note = request.form['note']
    image_file = None
    expense_name = generate_unique_sequence_number(Expense, Expense.name, length=8, prefix="EXP-")
    if amount :
        amount = float(amount)
    today_datetime = datetime.now()
    if file :
        image_file = file.read()

    new_expense = Expense(
        name=expense_name,
        purchase_event_id=purchase_event_id,
        amount=amount,
        note=note,
        image=image_file,
        created = today_datetime
    )
    db.session.add(new_expense)
    db.session.commit()
    return redirect(f"/expense/index?pe={purchase_event_id}")


@bp.route('/edit', methods=["POST","GET"])
def expense_edit():
    try :
        pe = request.args.get("pe")
        expense_id = request.args.get("expense_id")
        expense = Expense.query.get(int(expense_id))
        return render_template('expense/edit.html', purchase_event=pe, expense=expense)
    except Exception as e :
        print(e)

@bp.route('/update', methods=["POST","GET"])
def expense_update():
    try :
        purchase_event_id = request.form['purchase_event_id']
        file = request.files['image']
        amount = request.form['amount']
        note = request.form['note']
        expense_id = request.form['expense_id']
        image_file = None
        if file:
            image_file = file.read()
        expense = Expense.query.get(int(expense_id))
        if expense :
            if image_file :
                expense.image = image_file
            expense.amount = amount
            expense.note = note
        db.session.commit()
        return redirect(f"/expense/index?pe={purchase_event_id}")
    except Exception as e :
        print(e)

@bp.route('/money/add', methods=["POST","GET"])
def expense_money_add():
    try :
        purchase_event_id = request.form.get('purchase_event_id')
        expense_id = request.form.get('expense_id')
        amount = request.form.get('amount')
        type = request.form.get('type')
        note = request.form.get('note')
        amount = float(amount)
        if type.lower() == 'credit' :
            amount = -amount

        purchase_event_id = int(purchase_event_id)
        money_name = generate_unique_sequence_number(Money, Money.number, length=8, prefix="MO-")
        today_datetime = datetime.now()
        money = Money(amount=amount,note=note,purchase_event_id=purchase_event_id,number=money_name,expense_id=expense_id if expense_id else None, created = today_datetime)
        db.session.add(money)
        db.session.commit()
        return redirect(request.referrer)
    except Exception as e :
        print(e)



