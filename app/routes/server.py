import functools

import psutil
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response, send_from_directory, abort, make_response
)
import socket
from sqlalchemy import and_, create_engine
from flask import jsonify
from app.models.db import db
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.models_odoo import ResUserOdoo, ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, NfcappCommodityItemOdoo, NfcappCommodityOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.models import PurchaseEvent, User, PurchaseOrder, PurchaseOrderLine, Money
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
from dotenv import load_dotenv
import qrcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64


load_dotenv()
bp = Blueprint('server', __name__,url_prefix='/server')
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')

def get_local_ip():
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Connect to an external server (Google DNS)
        s.connect(('8.8.8.8', 80))
        # Get the local IP address
        local_ip = s.getsockname()[0]
    except Exception as e:
        # Handle exception and provide fallback
        local_ip = '127.0.0.1'
    finally:
        # Close the socket
        s.close()

    return local_ip

def generate_qr_code(data):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill='black', back_color='white')

    # Save the image to a BytesIO object
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    # Encode the image to base64
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_str


def generate_unique_sequence_number(model, column, length=4, prefix=""):
    sequence_number = prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    if not model.query.filter(column == sequence_number).first():
        return sequence_number


def get_current_ip():
    ip_addresses = {}
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if address.family == socket.AF_INET:
                ip_addresses[interface_name] = address.address

    if 'en0' in ip_addresses:  # macOS
        return ip_addresses.get('en0')
    elif 'Wi-Fi' in ip_addresses:  # windows
        return ip_addresses.get('Wi-Fi')
    else:
        return None


@bp.route('/sync', methods=["GET"])
@login_required
def sync_menu():
    count = {}
    count["product_odoo"] = ProductOdoo.query.count()
    count["purchase_order_odoo"] = PurchaseOrderOdoo.query.count()
    count["purchase_order_line_odoo"] = PurchaseOrderLineOdoo.query.count()
    count["farmer_odoo"] = NfcappFarmerOdoo.query.count()
    count["user_odoo"] = ResUserOdoo.query.count()
    count["commodity_odoo"] = NfcappCommodityOdoo.query.count()
    count["commodityitem_odoo"] = NfcappCommodityItemOdoo.query.count()
    count["station_odoo"] = NfcappStationOdoo.query.count()
    count["cluster_odoo"] = NfcappClusterOdoo.query.count()
    print(count)
    return render_template('server/sync.html', count=count)

@bp.route('/reset-db', methods=["GET"])
def reset_db():
    db.session.query(ProductOdoo).delete()
    db.session.query(PurchaseOrderOdoo).delete()
    db.session.query(PurchaseOrderLineOdoo).delete()
    db.session.query(NfcappFarmerOdoo).delete()
    db.session.query(NfcappCommodityOdoo).delete()
    db.session.query(NfcappCommodityItemOdoo).delete()
    db.session.query(NfcappStationOdoo).delete()
    db.session.query(NfcappClusterOdoo).delete()
    db.session.commit()

    return redirect(url_for('routes.server.sync_menu'))


@bp.route('/master/farmer', methods=["GET"])
def master_data_farmer():
    parent_id = request.args.get('parent_id',0, type=int)
    station_id = request.args.get('station_id', 0 , type=int)
    farmers = NfcappFarmerOdoo.query.filter_by(parent_id=parent_id).all()
    clusters = NfcappClusterOdoo.query.all()
    stations = NfcappStationOdoo.query.all()
    datas = []
    for farmer in farmers:
        data = {}
        data['farmer']=farmer
        data2 = []
        commodity_items = NfcappCommodityItemOdoo.query.filter(
            NfcappCommodityItemOdoo.farmer_id == farmer.odoo_id,
            NfcappCommodityItemOdoo.product_id.isnot(None)
        ).all()
        for commodity_item in commodity_items:
            data2.append(commodity_item)
        data['commodity_items'] = data2
        datas.append(data)

    return render_template('server/master_farmer.html',datas=datas, clusters=clusters, stations=stations, parent_id=parent_id, station_id=station_id)


@bp.route('/master/purchase-order', methods=["GET"])
def master_data_purchase_order():
    purchase_orders2 = PurchaseOrderOdoo.query.order_by(PurchaseOrderOdoo.odoo_id.desc()).all()
    data = []
    for po in purchase_orders2 :
        po_json = {}
        po_json['po'] = po
        data.append(po_json)
        po_order_line = PurchaseOrderLineOdoo.query.filter_by(order_id=int(po.odoo_id)).all()
        po_order_line_arr = []
        for order_line in po_order_line :
            order_line_json = {}
            order_line_json['order_line'] = order_line
            po_order_line_arr.append(order_line_json)
        po_json['order_lines'] = po_order_line_arr
    return render_template('server/master_po.html',purchase_data=data)

@bp.route('/master/backup', methods=["GET"])
def master_data_backup():
    return render_template('server/backup.html')

@bp.route('/master/download_backup', methods=["GET"])
def download_backup():
    today_datetime = datetime.now()
    instance_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'instance'))
    new_filename = "purchase-"+str(today_datetime)+".db"
    file_path = os.path.join(instance_directory, "purchase.db")
    try:
        # return send_from_directory(instance_directory, "purchase.db", as_attachment=True, attachment_filename=new_filename)
        with open(file_path, 'rb') as f:
            # Create a response
            response = make_response(f.read())
            # Set the headers to force download
            response.headers['Content-Type'] = 'application/octet-stream'
            response.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(new_filename)
            return response
    except FileNotFoundError:
        abort(404)

def allowed_file(filename):
    allowed_extensions = {'db'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@bp.route('master/upload_database', methods=['POST'])
def upload_database():

    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Define the path to the 'instance' directory within the route
        upload_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'instance'))
        file_path = os.path.join(upload_folder, "purchase.db")
        # Save the file, replacing any existing file
        file.save(file_path)
        return '''
        <script>alert("Purchase.db uploaded successfully");</script>
        <meta http-equiv="refresh" content="0; URL='/server/master/backup'">
        '''
        # flash(f'Purchase.db uploaded successfully')
        # return redirect(url_for('routes.server.master_data_backup'))


@bp.route('/purchase-order/view', methods=["POST","GET"])
def purchase_order_view():
    print(request)
    po_id = request.args.get("po")
    purchase_order = PurchaseOrderOdoo.query.get(po_id)
    return render_template('server/purchase_order_view.html', purchase_order=purchase_order)


@bp.route('/purchase-event/', methods=["GET"])
def purchase_event_list():
    po_id = request.args.get('po', 0, type=int)
    events = PurchaseEvent.query.filter_by(purchase_order_odoo_id=po_id).order_by(PurchaseEvent.id.desc()).all()
    purchase_order = PurchaseOrderOdoo.query.get(po_id)
    purchase_order_line = po_order_line = PurchaseOrderLineOdoo.query.filter_by(order_id=int(purchase_order.odoo_id)).all()
    event_ids = [event.id for event in events]
    orders = PurchaseOrder.query.filter(PurchaseOrder.purchase_event_id.in_(event_ids)).all()
    return render_template('server/purchase_event.html', events=events,po=po_id,purchase_order=purchase_order, orders=orders , purchase_order_line=purchase_order_line, NfcappFarmerOdoo=NfcappFarmerOdoo, ProductOdoo=ProductOdoo)



@bp.route('/purchase-event/create', methods=["POST","GET"])
def purchase_event_create_new():
    po_id = request.args.get('po', 0, type=int)

    po_list = PurchaseOrderOdoo.query.filter_by(id=po_id).first()

    return render_template('server/purchase_event_create.html', purchase_order=po_list)


@bp.route('/purchase-event/add', methods=["POST","GET"])
def purchase_event_add():
    date = request.form['date']
    note = request.form['note']
    purchase_order = request.form['purchase-order']
    po = PurchaseOrderOdoo.query.get(int(purchase_order))
    pe_name = generate_unique_sequence_number(PurchaseEvent, PurchaseEvent.name, length=4, prefix=po.name+"-")
    today_datetime = datetime.now()
    date = datetime.strptime(date, '%Y-%m-%d').date()
    purchase_event = PurchaseEvent(name=pe_name, note=note,created=today_datetime, date_stamp=date,purchase_order_odoo_id=purchase_order)
    db.session.add(purchase_event)
    db.session.commit()

    return redirect(url_for('routes.server.purchase_event_view', pe=purchase_event.id))

@bp.route('/purchase-event/details', methods=["POST","GET"])
def purchase_event_details():
    purchasers = ResUserOdoo.query.all()
    purchase_event_id = request.args.get("pe")
    purchase_event = PurchaseEvent.query.get(purchase_event_id)
    purchase_order = PurchaseOrderOdoo.query.get(purchase_event.purchase_order_odoo_id)
    return render_template('server/purchase_event_details.html', purchase_event=purchase_event, purchase_order=purchase_order)

@bp.route('/purchase-event/view', methods=["POST","GET"])
def purchase_event_view():
    purchasers = ResUserOdoo.query.all()
    base_url = "https://"+str(get_current_ip())+":5000/"
    base_url2 = "https://" + str(request.remote_addr) + ":5000/"



    purchase_event_id = request.args.get("pe")
    purchase_event = PurchaseEvent.query.get(purchase_event_id)
    local_ip = get_local_ip()
    data_purchase = f"{base_url}purchase/transaction?pe={purchase_event_id}"
    data_delivery = f"{base_url}delivery/index?pe={purchase_event_id}"
    data_cashier = f"{base_url2}cashier/index?pe={purchase_event_id}"
    qr_code_purchase = generate_qr_code(data_purchase)
    qr_code_delivery = generate_qr_code(data_delivery)
    qr_code_cashier = generate_qr_code(data_cashier)
    purchase_order = PurchaseOrderOdoo.query.get(purchase_event.purchase_order_odoo_id)

    payments = Money.query.filter_by(purchase_event_id=purchase_event.id).order_by(Money.created.asc())
    purchase_order_odoo = PurchaseOrderOdoo.query.get(purchase_event.purchase_order_odoo_id)
    return render_template('server/purchase_event_view.html', qr_code_cashier=qr_code_cashier,qr_code_delivery=qr_code_delivery,qr_code_purchase=qr_code_purchase,data_cashier=data_cashier,data_delivery=data_delivery,data_purchase=data_purchase,purchase_event=purchase_event,base_url=base_url, purchase_order=purchase_order,payments=payments, PurchaseOrder=PurchaseOrder,purchase_order_odoo=purchase_order_odoo)


@bp.route('/purchase-event/update', methods=["POST","GET"])
def purchase_event_update():
    # Retrieve updated data from the POST request
    id = request.form['event_id']
    date = request.form['date_stamp']
    note = request.form['note']
    po = request.form['purchase-order']
    event = PurchaseEvent.query.filter_by(id=id).first()
    if event:
        event.note = note
        event.date_stamp = datetime.strptime(date, '%Y-%m-%d').date()
        event.purchase_order_odoo_id = int(po) if po else None
        db.session.commit()
        return redirect("/server/purchase-event/view?pe="+str(event.id))
    else:
        return redirect("/server/purchase-event/view?pe="+str(event.id))


@bp.route('/purchase-event/delete', methods=["POST","GET"])
def purchase_event_delete():
    purchase_event_id = request.args.get("pe")
    print(purchase_event_id)

    # Retrieve the object from the database
    purchase_event = PurchaseEvent.query.get(purchase_event_id)

    if purchase_event:
        # Mark the object for deletion
        db.session.delete(purchase_event)

        # Commit the transaction to save the changes
        db.session.commit()

    return redirect(url_for('routes.server.purchase_event_list'))


@bp.route('/purchase-event/payments', methods=["POST","GET"])
def purchase_event_payments():
    purchase_event_id = request.args.get("pe")
    purchase_event = PurchaseEvent.query.get(purchase_event_id)
    payments = Money.query.filter_by(purchase_event_id=purchase_event.id).order_by(Money.created.asc())
    purchase_order_odoo = PurchaseOrderOdoo.query.get(purchase_event.purchase_order_odoo_id)
    return render_template('server/purchase_event_payments.html', purchase_event=purchase_event, payments=payments, PurchaseOrder=PurchaseOrder,purchase_order_odoo=purchase_order_odoo)


@bp.route('/money/add', methods=["POST","GET"])
def server_money_add():
    try :
        purchase_event_id = request.form.get('purchase_event_id')
        purchase_order_id = request.form.get('purchase_order_id')
        grand_total = request.form.get('grand_total')
        paid_amount = request.form.get('paid_amount')
        amount = request.form.get('amount')
        type = request.form.get('type')
        note = request.form.get('note')
        amount = float(amount)
        grand_total = float(grand_total)
        paid_amount = float(paid_amount)
        if type.lower() == 'credit' :
            amount = -amount

        purchase_event_id = int(purchase_event_id)

        today_datetime = datetime.now()
        difference = grand_total - paid_amount + amount
        if difference<=0 :
            amount2 = paid_amount - grand_total
            money_name1 = generate_unique_sequence_number(Money, Money.number, length=8, prefix="MO-")
            money1 = Money(amount=amount2,note=note,purchase_event_id=purchase_event_id,number=money_name1,purchase_order_id=purchase_order_id if purchase_order_id else None, created = today_datetime)
            db.session.add(money1)
            db.session.commit()
            money_name2 = generate_unique_sequence_number(Money, Money.number, length=8, prefix="MO-")
            money2 = Money(amount=difference,note="Rounding",purchase_event_id=purchase_event_id,number=money_name2,purchase_order_id=purchase_order_id if purchase_order_id else None, created = today_datetime)
            db.session.add(money2)
            db.session.commit()
        else :
            money_name = generate_unique_sequence_number(Money, Money.number, length=8, prefix="MO-")
            money = Money(amount=amount,note=note,purchase_event_id=purchase_event_id,number=money_name,purchase_order_id=purchase_order_id if purchase_order_id else None, created = today_datetime)
            db.session.add(money)
            db.session.commit()



        # db.session.add(money)

        return redirect(request.referrer)
    except Exception as e :
        print(e)

@bp.route('/money/add2', methods=["GET"])
def server_money_add2():
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

@bp.route('/test-print', methods=["GET"])
def server_test_print():
    return render_template('server/test_print.html')


@bp.route('/master/product', methods=["GET"])
def master_data_product():
    products = ProductOdoo.query.all()

    return render_template('server/master_product.html', products=products)


@bp.route('/master/commodity-item', methods=["GET"])
def master_data_commodity_item():
    commodity_id = request.args.get('commodity_id',0, type=int)
    station_id = request.args.get('station_id', 0 , type=int)
    commodities = NfcappCommodityOdoo.query.all()
    stations = NfcappStationOdoo.query.all()
    commodity_items = NfcappCommodityItemOdoo.query.filter_by(commodity_id=commodity_id).all()

    return render_template('server/master_commodity_item.html', commodity_items=commodity_items,
                           commodities=commodities, stations=stations, commodity_id=commodity_id, station_id=station_id)

