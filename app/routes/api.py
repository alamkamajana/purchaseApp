from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import requests
from app.models.models import ProductOdoo

load_dotenv()
bp = Blueprint('api_sync', __name__, url_prefix='/sync')
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')

@bp.route('/get-product')
def sync_get_product():
    try :
        # URL to send the POST request
        url = f"{odoo_base_url}/nfcapp-purchase/get-product"


        # Data you want to send (usually a dictionary)
        data = {
            'token': token,
        }


        # GET Request
        response = requests.get(url, data=data)
        response_json = response.json()
        for product in response_json :
            product_puid = product['puid']
            check_productodoo = ProductOdoo.query.filter_by(puid=product_puid)
            print(check_productodoo)


        return {}
    except Exception as e:
        print(e)
        return {"error": str(e)}