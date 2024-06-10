from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db
from .models import user_purchase_order_association
from.models import User


session = db.session

def get_local_time():
    return datetime.now()

class ProductOdoo(db.Model):
    __tablename__ = 'product_odoo'
    id = db.Column(db.Integer, primary_key=True)
    default_code = db.Column(db.String)
    active = db.Column(db.Boolean)
    product_tmpl_id = db.Column(db.Integer)
    barcode = db.Column(db.String)
    name = db.Column(db.String)
    volume = db.Column(db.Float)
    weight = db.Column(db.Float)
    type = db.Column(db.String)
    item_code = db.Column(db.String)
    commodity = db.Column(db.String)
    odoo_id = db.Column(db.Integer)
    create_date = db.Column(db.DateTime)
    write_date = db.Column(db.DateTime)
    sync_date = db.Column(db.DateTime, default=get_local_time, onupdate=get_local_time)

    def __repr__(self):
        return f'<ProductOdoo {self.default_code}>'

class NfcappFarmerOdoo(db.Model):
    __tablename__ = 'nfcapp_farmer_odoo'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer)
    parent_name = db.Column(db.String)
    station_id = db.Column(db.Integer)
    station_name = db.Column(db.String)
    code = db.Column(db.String)
    farmer_name = db.Column(db.String)
    farmer_role = db.Column(db.String)
    registration_date = db.Column(db.Date)
    contract_date = db.Column(db.Date)
    gender = db.Column(db.String)
    date_of_birth = db.Column(db.Date)
    phone_number = db.Column(db.String)
    active = db.Column(db.Boolean)
    no_ktp = db.Column(db.String)
    bank_akun = db.Column(db.String)
    bank_holder = db.Column(db.String)
    bank_name_name = db.Column(db.String)
    odoo_id = db.Column(db.Integer)
    certification_status_id = db.Column(db.Integer)
    certification_status_name = db.Column(db.String)
    create_date = db.Column(db.DateTime)
    write_date = db.Column(db.DateTime)
    sync_date = db.Column(db.DateTime, default=get_local_time, onupdate=get_local_time)


    def __repr__(self):
        return f'<Farmer {self.farmer_name}>'

class PurchaseOrderOdoo(db.Model):
    __tablename__ = 'purchase_order_odoo'
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String)
    name = db.Column(db.String)
    partner_id = db.Column(db.Integer)
    partner_name = db.Column(db.String)
    partner_ref = db.Column(db.String)
    analytic_account_id = db.Column(db.Integer)
    analytic_account_name = db.Column(db.String)
    manager_id = db.Column(db.Integer)
    manager_name = db.Column(db.String)
    currency_name = db.Column(db.String)
    date_approve = db.Column(db.Date)
    picking_type_name = db.Column(db.String)
    incoterm_name = db.Column(db.String)
    user_name = db.Column(db.String)
    payment_term_name = db.Column(db.String)
    odoo_id = db.Column(db.Integer)
    users = db.relationship('User', secondary=user_purchase_order_association, back_populates='purchase_orders')
    create_date = db.Column(db.DateTime)
    write_date = db.Column(db.DateTime)
    sync_date = db.Column(db.DateTime, default=get_local_time, onupdate=get_local_time)


    def calculate_grand_total(self):
        lines = PurchaseOrderLineOdoo.query.filter_by(order_id = self.odoo_id).all()
        return sum(line.product_qty * line.price_unit for line in lines)



    def __repr__(self):
        return f'<PurchaseOrderOdoo {self.name}>'

class PurchaseOrderLineOdoo(db.Model):
    __tablename__ = 'purchase_order_line_odoo'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    product_id = db.Column(db.Integer)
    product_name = db.Column(db.String)
    product_qty = db.Column(db.Float)
    qty_received = db.Column(db.Float)
    price_unit = db.Column(db.Float)
    date_planned = db.Column(db.Date)
    order_id = db.Column(db.Integer)
    order_name = db.Column(db.String)
    odoo_id = db.Column(db.Integer)
    create_date = db.Column(db.DateTime)
    write_date = db.Column(db.DateTime)
    sync_date = db.Column(db.DateTime, default=get_local_time, onupdate=get_local_time)


    def __repr__(self):
        return f'<PurchaseOrderLineOdoo {self.name}>'

class ResUserOdoo(db.Model):
    __tablename__ = 'res_user_odoo'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    name = db.Column(db.String)
    login = db.Column(db.String)
    company_id = db.Column(db.Integer)
    partner_id = db.Column(db.Integer)
    partner_name = db.Column(db.String)
    email = db.Column(db.Text)
    employee_id = db.Column(db.Integer)
    employee_name = db.Column(db.String)
    odoo_id = db.Column(db.Integer)
    create_date = db.Column(db.DateTime)
    write_date = db.Column(db.DateTime)
    sync_date = db.Column(db.DateTime, default=get_local_time, onupdate=get_local_time)

class NfcappCommodityOdoo(db.Model):
    __tablename__ = 'nfcapp_commodity_odoo'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    station_id = db.Column(db.Integer)
    station_name = db.Column(db.String)
    odoo_id = db.Column(db.Integer)
    create_date = db.Column(db.DateTime)
    write_date = db.Column(db.DateTime)
    sync_date = db.Column(db.DateTime, default=get_local_time, onupdate=get_local_time)

class NfcappCommodityItemOdoo(db.Model):
    __tablename__ = 'nfcapp_commodity_item_odoo'

    farmer_id = db.Column(db.Integer)
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String)
    desc = db.Column(db.String)
    certStatus = db.Column(db.String)
    commodity_id = db.Column(db.Integer)
    commodity_name = db.Column(db.String)
    variant = db.Column(db.String)
    commodity_name = db.Column(db.String)
    variant = db.Column(db.String)
    packing = db.Column(db.String)
    total_premium = db.Column(db.Integer)
    cu_number = db.Column(db.String)
    is_organic = db.Column(db.Boolean)
    is_ra_cert = db.Column(db.Boolean)
    color_name = db.Column(db.String)
    color_hex = db.Column(db.String)
    product_id = db.Column(db.Integer)
    product_id_code = db.Column(db.String)
    product_id_name = db.Column(db.String)
    product_name = db.Column(db.String)
    price = db.Column(db.Float)
    odoo_id = db.Column(db.Integer)
    create_date = db.Column(db.DateTime)
    write_date = db.Column(db.DateTime)
    sync_date = db.Column(db.DateTime, default=get_local_time, onupdate=get_local_time)

class NfcappStationOdoo(db.Model):
    __tablename__ = 'nfcapp_station_odoo'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    province = db.Column(db.String)
    gps_latitude = db.Column(db.Float)
    gps_longitude = db.Column(db.Float)
    is_testing = db.Column(db.Boolean)
    odoo_id = db.Column(db.Integer)
    create_date = db.Column(db.DateTime)
    write_date = db.Column(db.DateTime)
    sync_date = db.Column(db.DateTime, default=get_local_time, onupdate=get_local_time)

class NfcappClusterOdoo(db.Model):
    __tablename__ = 'nfcapp_cluster_odoo'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    station_id = db.Column(db.Integer)
    station_name = db.Column(db.String)
    coordinator = db.Column(db.String)
    code = db.Column(db.String)
    odoo_id = db.Column(db.Integer)
    create_date = db.Column(db.DateTime)
    write_date = db.Column(db.DateTime)
    sync_date = db.Column(db.DateTime, default=get_local_time, onupdate=get_local_time)
