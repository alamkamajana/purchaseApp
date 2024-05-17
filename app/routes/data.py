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

@bp.route('/master', methods=["GET"])
@login_required
def master_data():
    farmers = Farmer.query.all()
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