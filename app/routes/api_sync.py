from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import requests
from app.models.models_odoo import ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, ResUserOdoo, NfcappCommodityOdoo, NfcappCommodityItemOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.db import db

load_dotenv()
bp = Blueprint('api_sync', __name__, url_prefix='/sync')
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')


@bp.route('/', methods=["GET"])
def sync_menu():
    return render_template('master/sync.html')

@bp.route('/master_data', methods=["GET"])
def sync_master_data():
    return render_template('master/data.html')


@bp.route('/get-product-odoo')
def sync_get_product_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-product"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for product in response_json :
            product_puid = product['puid']
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
            check_productodoo = ProductOdoo.query.filter_by(puid=product_puid).first()
            if not check_productodoo :
                new_productodoo = ProductOdoo(puid=product_puid,active=active,barcode=barcode,default_code=default_code,product_tmpl_id=product_tmpl_id,name=name,volume=volume,weight=weight,type=type,item_code=item_code,commodity=commodity)
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
def sync_get_purchase_order():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-purchase-order"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for po in response_json :
            puid = po['puid']
            po_json = {k: v for k, v in po.items() if k != 'id'}
            check_po_odoo = PurchaseOrderOdoo.query.filter_by(puid=puid).first()
            if not check_po_odoo :
                new_po_odoo = PurchaseOrderOdoo(**po_json)
                db.session.add(new_po_odoo)

        db.session.commit()

        return {
            "message" : "Success",
            "status" : 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status":400}

@bp.route('/get-purchase-order-line-odoo')
def sync_get_purchase_order_line():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-purchase-order-line"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for po_line in response_json :
            puid = po_line['puid']
            po_line_json = {k: v for k, v in po_line.items() if k != 'id'}
            check_data = PurchaseOrderLineOdoo.query.filter_by(puid=puid).first()
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
def sync_get_farmer_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-nfcapp-farmer"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for farmer in response_json :
            puid = farmer['puid']
            farmer_json = {k: v for k, v in farmer.items() if k != 'id'}
            check_data = NfcappFarmerOdoo.query.filter_by(puid=puid).first()
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
def sync_user_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-res-user"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for user in response_json :
            puid = user['puid']
            user_json = {k: v for k, v in user.items() if k != 'id'}
            check_data = ResUserOdoo.query.filter_by(puid=puid).first()
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
def sync_commodity_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-commodity"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for commodity in response_json :
            puid = commodity['puid']
            commodity_json = {k: v for k, v in commodity.items() if k != 'id'}
            check_data = NfcappCommodityOdoo.query.filter_by(puid=puid).first()
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
def sync_commodityitem_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-commodityitem"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for commodity in response_json :
            puid = commodity['puid']
            commodity_json = {k: v for k, v in commodity.items() if k != 'id'}
            check_data = NfcappCommodityItemOdoo.query.filter_by(puid=puid).first()
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
def sync_station_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-station"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for station in response_json :
            puid = station['puid']
            station_json = {k: v for k, v in station.items() if k != 'id'}
            check_data = NfcappStationOdoo.query.filter_by(puid=puid).first()
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
def sync_cluster_odoo():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-cluster"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for cluster in response_json :
            puid = cluster['puid']
            cluster_json = {k: v for k, v in cluster.items() if k != 'id'}
            check_data = NfcappClusterOdoo.query.filter_by(puid=puid).first()
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