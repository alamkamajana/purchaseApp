from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import aiohttp
import asyncio
import ssl
import requests
from app.models.models_odoo import ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, ResUserOdoo, \
    NfcappCommodityOdoo, NfcappCommodityItemOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.models import User
from app.models.db import db
from .auth import login_required

load_dotenv()
bp = Blueprint('sync', __name__, url_prefix='/sync')
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')


def format_date_obj(date_obj):
    try:
        dateku = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S.%f')
    except:
        dateku=None
    return dateku



@bp.route('/get-product-odoo')
@login_required
def sync_get_product_odoo():
    try:
        url = f"{odoo_base_url}/nfcapp-purchase/get-product"
        data = {'token': token, 'odoo_user_id': session['user_odoo_id']}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for product in response_json:
            product_oid = product['odoo_id']
            product_json = {k: v for k, v in product.items() if k != 'id'}
            product_json['write_date'] = format_date_obj(product_json['write_date'])
            check_productodoo = ProductOdoo.query.filter_by(odoo_id=product_oid).first()
            if check_productodoo:
              for key, value in product_json.items():
                    setattr(check_productodoo, key, value)

            else:
                new_product_odoo = ProductOdoo(**product_json)
                print(new_product_odoo)
                db.session.add(new_product_odoo)

        db.session.commit()

        return {
            "message": "Success",
            "status": 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status": 400}
    

@bp.route('/get-purchase-order-odoo')
@login_required
def sync_get_purchase_order():
    try:
        url = f"{odoo_base_url}/nfcapp-purchase/get-purchase-order"
        data = {'token': token, 'odoo_user_id': session['user_odoo_id']}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for po in response_json:
            oid = po['odoo_id']
            po_json = {k: v for k, v in po.items() if k != 'id'}
            po_json['date_approve'] = None
            po_json['write_date'] = format_date_obj(po_json['write_date'])
            check_po_odoo = PurchaseOrderOdoo.query.filter_by(odoo_id=oid).first()

            if check_po_odoo:
                for key, value in po_json.items():
                    setattr(check_po_odoo, key, value)

            else:
                user = User.query.filter_by(user_odoo_id=session['user_odoo_id']).first()
                new_po_odoo = PurchaseOrderOdoo(**po_json)
                db.session.add(new_po_odoo)
                user.purchase_orders.append(new_po_odoo)

        db.session.commit()

        return {
            "message": "Success",
            "status": 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status": 400}


@bp.route('/get-purchase-order-line-odoo')
@login_required
def sync_get_purchase_order_line():
    try:
        url = f"{odoo_base_url}/nfcapp-purchase/get-purchase-order-line"
        data = {'token': token, 'odoo_user_id': session['user_odoo_id']}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for po_line in response_json:
            oid = po_line['odoo_id']
            po_line_json = {k: v for k, v in po_line.items() if k != 'id'}
            po_line_json['date_planned'] = None
            po_line_json['write_date'] = format_date_obj(po_line_json['write_date'])
            check_data = PurchaseOrderLineOdoo.query.filter_by(odoo_id=oid).first()

            if check_data:
                for key, value in po_line_json.items():
                    setattr(check_data, key, value)
            else:
                new_data = PurchaseOrderLineOdoo(**po_line_json)
                db.session.add(new_data)

        db.session.commit()

        return {
            "message": "Success",
            "status": 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status": 400}


@bp.route('/get-farmer-odoo')
@login_required
def sync_get_farmer_odoo():
    try:
        url = f"{odoo_base_url}/nfcapp-purchase/get-nfcapp-farmer"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for farmer in response_json:
            oid = farmer['odoo_id']
            farmer_json = {k: v for k, v in farmer.items() if not k in ['id', 'commodity_items']}


            farmer_json['registration_date'] = None
            farmer_json['contract_date'] = None
            farmer_json['date_of_birth'] = None
            farmer_json['write_date'] = format_date_obj(farmer_json['write_date'])

            check_data = NfcappFarmerOdoo.query.filter_by(odoo_id=oid).first()
            if check_data:
                if check_data.write_date != farmer_json['write_date']:
                    for key, value in farmer_json.items():
                        setattr(check_data, key, value)
            else:
                new_data = NfcappFarmerOdoo(**farmer_json)
                db.session.add(new_data)
                for commodity in farmer['commodity_items']:
                    oid = commodity['odoo_id']
                    commodity_json = {k: v for k, v in commodity.items() if k != 'id'}
                    # print(commodity_json)

                    commodity_json['write_date'] = format_date_obj(commodity_json['write_date'])

                    check_data2 = NfcappCommodityItemOdoo.query.filter_by(odoo_id=oid,
                                                                          farmer_id=farmer['odoo_id']).first()
                    if check_data2:
                        if check_data2.write_date != commodity_json['write_date']:
                            for key, value in commodity_json.items():
                                setattr(check_data2, key, value)
                    else:
                        new_data2 = NfcappCommodityItemOdoo(**commodity_json)
                        db.session.add(new_data2)

        db.session.commit()

        return {
            "message": "Success",
            "status": 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status": 400}


@bp.route('/get-user-odoo')
@login_required
def sync_user_odoo():
    try:
        url = f"{odoo_base_url}/nfcapp-purchase/get-res-user"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for user in response_json:
            oid = user['odoo_id']

            user_json = {k: v for k, v in user.items() if k != 'id'}


            user_json['write_date'] = format_date_obj(user_json['write_date'])
            check_data = ResUserOdoo.query.filter_by(odoo_id=oid).first()

            if check_data:
                for key, value in user_json.items():
                    setattr(check_data, key, value)

            else:
                new_data = ResUserOdoo(**user_json)
                db.session.add(new_data)

        db.session.commit()

        return {
            "message": "Success",
            "status": 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status": 400}


@bp.route('/get-commodity-odoo')
@login_required
def sync_commodity_odoo():
    try:
        url = f"{odoo_base_url}/nfcapp-purchase/get-commodity"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for commodity in response_json:
            oid = commodity['odoo_id']
            commodity_json = {k: v for k, v in commodity.items() if k != 'id'}

            commodity_json['write_date'] = format_date_obj(commodity_json['write_date'])

            check_data = NfcappCommodityOdoo.query.filter_by(odoo_id=oid).first()
            if check_data:
                for key, value in commodity_json.items():
                    setattr(check_data, key, value)

            else:
                new_data = NfcappCommodityOdoo(**commodity_json)
                db.session.add(new_data)

        db.session.commit()

        return {
            "message": "Success",
            "status": 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status": 400}


@bp.route('/get-commodityitem-odoo')
@login_required
def sync_commodityitem_odoo():
    try:
        url = f"{odoo_base_url}/nfcapp-purchase/get-commodityitem"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for commodity in response_json:
            oid = commodity['odoo_id']
            commodity_json = {k: v for k, v in commodity.items() if k != 'id'}

            commodity_json['write_date'] = format_date_obj(commodity_json['write_date'])
            check_data = NfcappCommodityItemOdoo.query.filter_by(odoo_id=oid).first()

            if check_data:
                for key, value in commodity_json.items():
                    setattr(check_data, key, value)

            else:
                new_data = NfcappCommodityItemOdoo(**commodity_json)
                db.session.add(new_data)

        db.session.commit()

        return {
            "message": "Success",
            "status": 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status": 400}


@bp.route('/get-station-odoo')
@login_required
def sync_station_odoo():
    try:
        url = f"{odoo_base_url}/nfcapp-purchase/get-station"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for station in response_json:
            oid = station['odoo_id']
            station_json = {k: v for k, v in station.items() if k != 'id'}
            station_json['write_date'] = format_date_obj(station_json['write_date'])
            check_data = NfcappStationOdoo.query.filter_by(odoo_id=oid).first()
            if check_data:
                for key, value in station_json.items():
                    setattr(check_data, key, value)
            else:
                new_data = NfcappStationOdoo(**station_json)
                db.session.add(new_data)

        db.session.commit()

        return {
            "message": "Success",
            "status": 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status": 400}


@bp.route('/get-cluster-odoo')
@login_required
def sync_cluster_odoo():
    try:
        url = f"{odoo_base_url}/nfcapp-purchase/get-cluster"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for cluster in response_json:
            oid = cluster['odoo_id']
            cluster_json = {k: v for k, v in cluster.items() if k != 'id'}

            cluster_json['write_date'] = format_date_obj(cluster_json['write_date'])
            check_data = NfcappClusterOdoo.query.filter_by(odoo_id=oid).first()
            if check_data:
                for key, value in cluster_json.items():
                    setattr(check_data, key, value)
            else:
                new_data = NfcappClusterOdoo(**cluster_json)
                db.session.add(new_data)



        db.session.commit()

        return {
            "message": "Success",
            "status": 200
        }
    except Exception as e:
        print(e)
        return {"message": str(e), "status": 400}


#
# def download_image(url, save_dir):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an exception for HTTP errors
#         filename = os.path.join(save_dir)
#         with open(filename, 'wb') as f:
#             f.write(response.content)
#         return {"url": url, "status": "success", "filename": filename}
#     except requests.exceptions.RequestException as e:
#         return {"url": url, "status": "error", "message": str(e)}
@bp.route('/get-farmer-photo')
@login_required
def sync_farmer_photo():
    farmers = NfcappFarmerOdoo.query.all()
    odoo_url = "https://odoo.tripper.com"

    async def download_image(session, url, path):
        async with session.get(url, ssl=False) as response:
            if response.status == 200:
                with open(path, 'wb') as f:
                    f.write(await response.read())
            else:
                print(f"Failed to download image from {url}")

    async def download_all_images():
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with aiohttp.ClientSession() as session:
            tasks = []
            for farmer in farmers:
                url = f"{odoo_url}/nfcapp/web/image?model=nfcapp.farmer&id={farmer.odoo_id}&field=photo"
                path = os.path.join("./app/static/image", f"{farmer.odoo_id}.png")
                tasks.append(download_image(session, url, path))
            await asyncio.gather(*tasks)

    # Run the asynchronous function using asyncio.run
    asyncio.run(download_all_images())
    return {
        "message": "Success",
        "status": 200
    }
