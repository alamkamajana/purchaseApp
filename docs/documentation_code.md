`from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from dotenv import load_dotenv
import os
import requests
from app.models.models_odoo import ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo, ResUserOdoo, NfcappCommodityOdoo, NfcappCommodityItemOdoo, NfcappStationOdoo, NfcappClusterOdoo
from app.models.db import db
from .auth import login_required`



