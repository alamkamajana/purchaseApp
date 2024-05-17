# app/models/__init__.py
from .db import db
from .models_odoo import ProductOdoo, NfcappFarmerOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, ResUserOdoo, NfcappCommodityOdoo, NfcappCommodityItemOdoo, NfcappStationOdoo, NfcappClusterOdoo
from .models import User,UserSession, Farmer, Product, PurchaseEvent, PurchaseOrder, PurchaseOrderLine, Payment, DeliveryOrder
