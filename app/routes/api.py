from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import requests
from app.models.models_odoo import ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, ResUserOdoo, NfcappCommodityOdoo, NfcappCommodityItemOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.db import db

load_dotenv()
bp = Blueprint('api', __name__,)
odoo_base_url = os.getenv('BASE_URL_ODOO')
token = os.getenv('TOKEN')

@bp.route('/')
def main_page():
    try :
        return {}
    except Exception as e:
        print(e)
        return {"message": str(e), "status":400}