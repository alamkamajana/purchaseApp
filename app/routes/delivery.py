from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import requests
from app.models.models_odoo import ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, ResUserOdoo, NfcappCommodityOdoo, NfcappCommodityItemOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.db import db
from app.models.models import User, PurchaseOrder, PurchaseEvent, DeliveryOrder
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
    pe_list = PurchaseEvent.query.all()
    do_list = DeliveryOrder.query.all()
    return render_template('delivery/delivery.html', pe_list=pe_list, do_list=do_list)

@bp.route('/create', methods=["POST","GET"])
@login_required
def delivery_create():
    try :
        data = request.get_json()

        driver = data['driver']
        vehicle = data['vehicle_number']
        pe = data['pe']
        do_name = generate_unique_sequence_number(DeliveryOrder, DeliveryOrder.name, length=8, prefix="DO-")
        today_datetime = datetime.now()

        current_user_session = session['user_odoo_id']
        current_user = User.query.filter_by(user_odoo_id=int(current_user_session) if current_user_session else None).first()
        current_user_odoo_id = current_user.user_odoo_id if current_user else None
        new_do = DeliveryOrder(name=do_name,driver=driver,vehicle_number=vehicle,purchase_event_id=int(pe), created=today_datetime, create_odoo_id=current_user_odoo_id)
        db.session.add(new_do)
        db.session.commit()
        return jsonify(do=new_do.id,status=200)
    except Exception as e :
        print(e)



