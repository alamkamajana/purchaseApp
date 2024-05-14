from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import requests
from app.models.models import ProductOdoo, db

load_dotenv()
bp = Blueprint('api_sync', __name__, url_prefix='/sync')
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')

@bp.route('/get-product')
def sync_get_product():
    try :
        url = f"{odoo_base_url}/nfcapp-purchase/get-product"
        data = {'token': token}

        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for product in response_json :
            product_puid = str(product['puid'])
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