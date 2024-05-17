import functools
import os
import click
import json


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flask import jsonify
from app.models.db import db
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.models_odoo import ResUserOdoo, ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo
from app.models.models import PurchaseEvent, Transaction, Farmer
from .auth import login_required

bp = Blueprint('select', __name__, url_prefix='/select')


@bp.route('/selectpickerUser', methods=["GET"])
@login_required
def selectpickerUser():
    query = request.args.get('q')

    user_list = ResUserOdoo.query.filter(ResUserOdoo.login.ilike(f'%{query}%')).all()

    res_user = [{
        "id": user.id,
        "text": user.name,
    } for user in user_list]

    # res_users.append({
    #     "id": "all",
    #     "text": "All",
    # })

    return json.dumps(res_user)


@bp.route('/selectpickerPo', methods=["GET"])
@login_required
def selectpickerPo():
    query = request.args.get('q')

    po_list = PurchaseOrderOdoo.query.filter(PurchaseOrderOdoo.name.ilike(f'%{query}%')).order_by(
        PurchaseOrderOdoo.id.desc()).all()

    res_po = [{
        "id": po.id,
        "text": po.name,
    } for po in po_list]

    # res_users.append({
    #     "id": "all",
    #     "text": "All",
    # })

    return json.dumps(res_po)


@bp.route('/selectpickerPurchaseEvent', methods=["GET"])
@login_required
def selectpickerPurchaseEvent():
    query = request.args.get('q')

    event_list = PurchaseEvent.query.filter(PurchaseEvent.name.ilike(f'%{query}%')).order_by(
        PurchaseEvent.id.desc()).all()

    res_event = [{
        "id": event.id,
        "text": event.name,
    } for event in event_list]

    # res_users.append({
    #     "id": "all",
    #     "text": "All",
    # })

    return json.dumps(res_event)


@bp.route('/selectpickerFarmer', methods=["GET"])
@login_required
def selectpickerFarmer():
    query = request.args.get('q')

    farmer_list = Farmer.query.filter(Farmer.farmer_name.ilike(f'%{query}%')).order_by(
        Farmer.farmer_name).all()

    res_farmer = [{
        "id": farmer.id,
        "text": farmer.farmer_name,
    } for farmer in farmer_list]

    return json.dumps(res_farmer)


@bp.route('/selectpickerProduct', methods=["GET"])
@login_required
def selectpickerProduct():
    query = request.args.get('q')

    product_list = ProductOdoo.query.filter(ProductOdoo.name.ilike(f'%{query}%')).order_by(
        ProductOdoo.name).all()

    res_product = [{
        "id": product.id,
        "text": product.name,
    } for product in product_list]

    return json.dumps(res_product)

