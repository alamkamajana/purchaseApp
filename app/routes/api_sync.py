from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import requests
from app.models.models_odoo import ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, ResUserOdoo, NfcappCommodityOdoo, NfcappCommodityItemOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.models import Farmer, User, Product
from app.models.db import db
from .auth import login_required

load_dotenv()
bp = Blueprint('api_sync', __name__, url_prefix='/sync')
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')

@bp.route('/get-product-odoo')
@login_required
def sync_get_product_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-product"
        data = {'token': token, 'odoo_user_id' : session['user_odoo_id']}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for product in response_json :
            product_oid = product['odoo_id']
            active = product['active']
            barcode = product['barcode']
            default_code = product['default_code']
            product_tmpl_id = product['product_tmpl_id']
            name = product['name']
            volume = product['volume']
            weight = product['weight']
            type = product['type']
            item_code = product['item_code']
            commodity = product['commodity']
            check_productodoo = ProductOdoo.query.filter_by(odoo_id=product_oid).first()
            if not check_productodoo :
                new_productodoo = ProductOdoo(odoo_id=product_oid,active=active,barcode=barcode,default_code=default_code,product_tmpl_id=product_tmpl_id,name=name,volume=volume,weight=weight,type=type,item_code=item_code,commodity=commodity)
                db.session.add(new_productodoo)

        db.session.commit()

        return {
            "message" : "Success",
            "status" : 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status":400}


@bp.route('/get-purchase-order-odoo')
@login_required
def sync_get_purchase_order():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-purchase-order"
        data = {'token': token,'odoo_user_id' : session['user_odoo_id']}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for po in response_json :
            oid = po['odoo_id']
            po_json = {k: v for k, v in po.items() if k != 'id'}
            check_po_odoo = PurchaseOrderOdoo.query.filter_by(odoo_id=oid).first()
            if not check_po_odoo :
                user = User.query.filter_by(user_odoo_id=session['user_odoo_id']).first()
                new_po_odoo = PurchaseOrderOdoo(**po_json)
                db.session.add(new_po_odoo)
                user.purchase_orders.append(new_po_odoo)

        db.session.commit()

        return {
            "message" : "Success",
            "status" : 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status":400}

@bp.route('/get-purchase-order-line-odoo')
@login_required
def sync_get_purchase_order_line():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-purchase-order-line"
        data = {'token': token, 'odoo_user_id' : session['user_odoo_id']}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for po_line in response_json :
            oid = po_line['odoo_id']
            po_line_json = {k: v for k, v in po_line.items() if k != 'id'}
            check_data = PurchaseOrderLineOdoo.query.filter_by(odoo_id=oid).first()
            if not check_data :
                new_data = PurchaseOrderLineOdoo(**po_line_json)
                db.session.add(new_data)

        db.session.commit()

        return {
            "message" : "Success",
            "status" : 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status":400}


@bp.route('/get-farmer-odoo')
@login_required
def sync_get_farmer_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-nfcapp-farmer"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for farmer in response_json :
            oid = farmer['odoo_id']
            farmer_json = {k: v for k, v in farmer.items() if k != 'id'}
            check_data = NfcappFarmerOdoo.query.filter_by(odoo_id=oid).first()
            if not check_data :
                new_data = NfcappFarmerOdoo(**farmer_json)
                db.session.add(new_data)

        db.session.commit()

        return {
            "message" : "Success",
            "status" : 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status":400}

@bp.route('/get-user-odoo')
@login_required
def sync_user_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-res-user"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for user in response_json :
            oid = user['odoo_id']
            user_json = {k: v for k, v in user.items() if k != 'id'}
            check_data = ResUserOdoo.query.filter_by(odoo_id=oid).first()
            if not check_data :
                new_data = ResUserOdoo(**user_json)
                db.session.add(new_data)

        db.session.commit()

        return {
            "message" : "Success",
            "status" : 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status":400}


@bp.route('/get-commodity-odoo')
@login_required
def sync_commodity_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-commodity"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for commodity in response_json :
            oid = commodity['odoo_id']
            commodity_json = {k: v for k, v in commodity.items() if k != 'id'}
            check_data = NfcappCommodityOdoo.query.filter_by(odoo_id=oid).first()
            if not check_data :
                new_data = NfcappCommodityOdoo(**commodity_json)
                db.session.add(new_data)

        db.session.commit()

        return {
            "message" : "Success",
            "status" : 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status":400}


@bp.route('/get-commodityitem-odoo')
@login_required
def sync_commodityitem_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-commodityitem"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for commodity in response_json :
            oid = commodity['odoo_id']
            commodity_json = {k: v for k, v in commodity.items() if k != 'id'}
            check_data = NfcappCommodityItemOdoo.query.filter_by(odoo_id=oid).first()
            if not check_data :
                new_data = NfcappCommodityItemOdoo(**commodity_json)
                db.session.add(new_data)

        db.session.commit()

        return {
            "message" : "Success",
            "status" : 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status":400}


@bp.route('/get-station-odoo')
@login_required
def sync_station_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-station"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for station in response_json :
            oid = station['odoo_id']
            station_json = {k: v for k, v in station.items() if k != 'id'}
            check_data = NfcappStationOdoo.query.filter_by(odoo_id=oid).first()
            if not check_data :
                new_data = NfcappStationOdoo(**station_json)
                db.session.add(new_data)

        db.session.commit()

        return {
            "message" : "Success",
            "status" : 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status":400}

@bp.route('/get-cluster-odoo')
@login_required
def sync_cluster_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-cluster"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for cluster in response_json :
            oid = cluster['odoo_id']
            cluster_json = {k: v for k, v in cluster.items() if k != 'id'}
            check_data = NfcappClusterOdoo.query.filter_by(odoo_id=oid).first()
            if not check_data :
                new_data = NfcappClusterOdoo(**cluster_json)
                db.session.add(new_data)

        db.session.commit()

        return {
            "message" : "Success",
            "status" : 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status":400}


# @bp.route('/sync-with-odoo')
# def sync_with_odoo():
#     try :
#         farmer_odoo = NfcappFarmerOdoo.query.all()
#         station_odoo = NfcappStationOdoo.query.all()
#         cluster_odoo = NfcappClusterOdoo.query.all()
#         commodity_odoo = NfcappCommodityOdoo.query.all()
#         commodityitem_odoo = NfcappCommodityItemOdoo.query.filter(NfcappCommodityItemOdoo.product_id != None).all()
#         product_odoo = ProductOdoo.query.all()
#
#         # item_id_arr = []
#         # for item in commodityitem_odoo :
#         #     item_id_arr.append(item.product_id)
#
#         for farmer in farmer_odoo :
#             farmer_name = farmer.farmer_name
#             farmer_code = farmer.code
#             check_farmer = Farmer.query.filter_by(farmer_odoo_id=farmer.id).first()
#             if not check_farmer :
#                 new_farmer = Farmer(farmer_name=farmer_name,farmer_code=farmer_code,farmer_odoo_id=farmer.id)
#                 db.session.add(new_farmer)
#
#         db.session.commit()
#
#         for new_farmer in Farmer.query.all():
#             farmer_odoo = NfcappFarmerOdoo.query.filter_by(id=new_farmer.farmer_odoo_id).first()
#             farmer_odoo_cluster = farmer_odoo.parent_id
#             # print(farmer_odoo_cluster)
#             cluster_odoo = NfcappClusterOdoo.query.filter_by(id=farmer_odoo_cluster).first()
#             # new_farmer_station = None
#             # if cluster_odoo is not False:
#             #     new_farmer_station = cluster_odoo
#             #     print(new_farmer_station)
#
#         resp = {
#             "message" : "Success",
#             "status" : 200
#         }
#         return resp
#     except Exception as e:
#         print(e)
#         return {"message": str(e), "status": 400}


@bp.route('/sync-with-odoo')
@login_required
def sync_with_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/sync-with-odoo"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()

        for farmer in response_json :
            check_data = Farmer.query.filter_by(odoo_id=farmer['odoo_id']).first()
            if not check_data :
                farmer_json = {}
                farmer_json['odoo_id'] = farmer['odoo_id']
                farmer_json['farmer_name'] = farmer['farmer_name']
                farmer_json['farmer_code'] = farmer['farmer_name']
                farmer_json['farmer_name'] = farmer['farmer_name']
                farmer_json['item_code_list'] = farmer['item_code_list']
                new_data = Farmer(**farmer_json)
                db.session.add(new_data)

        db.session.commit()


        resp = {
            "message" : "Success",
            "status" : 200
        }
        return resp
    except Exception as e:
        print(e)
        return {"message": str(e), "status": 400}