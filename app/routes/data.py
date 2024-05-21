from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import requests
from app.models.models_odoo import ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, ResUserOdoo, NfcappCommodityOdoo, NfcappCommodityItemOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.db import db
from app.models.models import Farmer
from .auth import login_required
import ast

load_dotenv()
bp = Blueprint('data', __name__, url_prefix='/data')
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')


@bp.route('/sync', methods=["GET"])
@login_required
def sync_menu():
    return render_template('data/sync.html')

@bp.route('/master2', methods=["GET"])
@login_required
def master_data2():
    parent_id = request.args.get('parent-id', type=int)
    farmers = NfcappFarmerOdoo.query.filter_by(parent_id=parent_id).all()

    datas = []


    for farmer in farmers:
        data = {}
        data['farmer']=farmer
        data2 = []
        commodity_items = NfcappCommodityItemOdoo.query.filter_by(farmer_id=farmer.odoo_id).all()
        for commodity_item in commodity_items:
            data2.append(commodity_item)
        data['commodity_items'] = data2
        datas.append(data)

    return render_template('data/master2.html',datas=datas)




@bp.route('/master', methods=["GET"])
@login_required
def master_data():
    farmers = Farmer.query.limit(100).all()
    data = []
    for farmer in farmers :
        farmer_json = {}
        farmer_json['id'] = farmer.id
        farmer_json['odoo_id'] = farmer.odoo_id
        farmer_json['farmer_name'] = farmer.farmer_name
        # farmer_json['item_code_list'] = list(ast.literal_eval(farmer.item_code_list)) if farmer.item_code_list else None
        farmer_item_code = list(ast.literal_eval(farmer.item_code_list)) if farmer.item_code_list else None
        farmer_item_product = []
        for item  in farmer_item_code :
            item_code_json = {}
            commodityitem = NfcappCommodityItemOdoo.query.filter_by(odoo_id=int(item)).first()
            product = None
            if commodityitem.product_id :
                product_search = ProductOdoo.query.filter_by(odoo_id=int(commodityitem.product_id)).first()
                product = product_search.name
            item_code_json['item'] = commodityitem.code
            item_code_json['product'] = product
            farmer_item_product.append(item_code_json)

            farmer_json['item_code_list'] = farmer_item_product

            # print(commodityitem)
        data.append(farmer_json)

    return render_template('data/master.html',farmer_data=data)


@bp.route('/purchase-order', methods=["GET"])
@login_required
def show_purchase_order():
    purchase_orders = PurchaseOrderOdoo.query.order_by(PurchaseOrderOdoo.odoo_id.desc()).all()
    data = []
    for po in purchase_orders :
        po_json = {}
        po_json['id'] = po.id
        po_json['name'] = po.name
        data.append(po_json)
        po_order_line = PurchaseOrderLineOdoo.query.filter_by(order_id=int(po.odoo_id)).all()
        po_order_line_arr = []
        for order_line in po_order_line :
            order_line_json = {}
            order_line_json['product_name'] = order_line.product_name
            order_line_json['price_unit'] = order_line.price_unit
            order_line_json['product_qty'] = order_line.product_qty
            po_order_line_arr.append(order_line_json)
        po_json['order_line'] = po_order_line_arr

    return render_template('data/purchase.html',purchase_data=data)