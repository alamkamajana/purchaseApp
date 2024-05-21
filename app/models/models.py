from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db

session = db.session

user_purchase_order_association = db.Table('user_purchase_order_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('purchase_order_odoo_id', db.Integer, db.ForeignKey('purchase_order_odoo.id'), primary_key=True)
)

farmer_product_association = db.Table('farmer_product_association',
    db.Column('farmer_id', db.Integer, db.ForeignKey('farmer.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)


class MasterFarmer(db.Model):
    __tablename__ = 'master_farmer'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    farmer_name = db.Column(db.String(120))
    odoo_id = db.Column(db.Integer)
    parent_id = db.Column(db.Integer)
    station_id = db.Column(db.Integer)




class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120))
    session = db.Column(db.String(120))
    is_active = db.Column(db.Boolean)
    station = db.Column(db.String)
    user_odoo_id = db.Column(db.Integer)
    purchase_orders = db.relationship('PurchaseOrderOdoo', secondary=user_purchase_order_association,
                                      back_populates='users')



    def __repr__(self):
        return '<User %r>' % self.username

class UserSession(db.Model):
    __tablename__ = 'user_session'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    session = db.Column(db.String(120))
    action = db.Column(db.String(120))
    device = db.Column(db.String)
    mac_address = db.Column(db.String)
    ip_address_local = db.Column(db.String)
    ip_address_external = db.Column(db.String)
    date = db.Column(db.DateTime)



class Farmer(db.Model):
    __tablename__ = 'farmer'
    id = db.Column(db.Integer, primary_key=True)
    farmer_name = db.Column(db.String(128))
    farmer_code = db.Column(db.String(64))
    products = db.relationship('Product', back_populates='farmer', lazy='dynamic')
    item_code_list = db.Column(db.Text)
    odoo_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Farmer %r>' % self.farmer_name

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String)
    product_name = db.Column(db.String)
    itemcode_code = db.Column(db.String)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))
    farmer = db.relationship('Farmer', back_populates='products')
    item_code_odoo_id = db.Column(db.Integer)
    product_odoo_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey('product_odoo.id'))
    itemcode_id = db.Column(db.Integer, db.ForeignKey('nfcapp_commodity_item_odoo.id'))


class PurchaseEvent(db.Model):
    __tablename__ = 'purchase_event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    fund = db.Column(db.Float, default=100000)
    ics = db.Column(db.String)
    purchaser_id = db.Column(db.Integer, db.ForeignKey('res_user_odoo.id'))
    purchaser = db.relationship('ResUserOdoo', foreign_keys=[purchaser_id], backref=db.backref('purchaser_events', lazy=True))
    cashier_id = db.Column(db.Integer, db.ForeignKey('res_user_odoo.id'))
    cashier = db.relationship('ResUserOdoo', foreign_keys=[cashier_id], backref=db.backref('cashier_events', lazy=True))
    ap_name = db.Column(db.String)
    ip_address = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False)
    purchase_order_odoo_id = db.Column(db.Integer, db.ForeignKey('purchase_order_odoo.id'))
    purchase_order_odoo = db.relationship('PurchaseOrderOdoo', foreign_keys=[purchase_order_odoo_id], backref=db.backref('purchase_events', lazy=True))
    purchase_orders = db.relationship('PurchaseOrder', back_populates='purchase_event', lazy='dynamic')
    payments = db.relationship('Payment', back_populates='purchase_event', lazy='dynamic')

    def __init__(self, fund, ics, purchaser_id, cashier_id, purchase_order_odoo_id, ap_name):
        self.fund = fund
        self.ics = ics
        self.purchaser_id = purchaser_id
        self.cashier_id = cashier_id
        self.purchase_order_odoo_id = purchase_order_odoo_id
        self.ip_address = request.remote_addr
        self.ap_name = ap_name
        self.created_at = datetime.utcnow()
        self.generate_name()

    def generate_name(self):
        # Get current date in the format YYYYMMDD
        date_str = self.created_at.strftime('%Y%m%d')
        # Count existing posts for the current date
        post_count = PurchaseEvent.query.filter(
            PurchaseEvent.created_at >= datetime.combine(self.created_at.date(), datetime.min.time())).count()
        # Set the name using the format PE-date-index
        self.name = f"PE{date_str}-{post_count + 1}"

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    receipt_number = db.Column(db.String(64))
    purchase_order_lines = db.relationship('PurchaseOrderLine', back_populates='purchase_order', lazy='dynamic')
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))
    status = db.Column(db.String(64))
    purchase_event_id = db.Column(db.Integer, db.ForeignKey('purchase_event.id'))
    purchase_event = db.relationship('PurchaseEvent', back_populates='purchase_orders')


class PurchaseOrderLine(db.Model):
    __tablename__ = 'purchase_order_line'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product_odoo_id = db.Column(db.Integer, db.ForeignKey('product_odoo.id'))
    qty = db.Column(db.Float)
    unit_price = db.Column(db.Float)
    barcode = db.Column(db.String)
    subtotal = db.Column(db.Float)
    currency = db.Column(db.String)
    delivery_order_id = db.Column(db.Integer, db.ForeignKey('delivery_order.id'))
    delivery_order = db.relationship('DeliveryOrder', back_populates='purchase_order_lines')
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'))
    purchase_order = db.relationship('PurchaseOrder', back_populates='purchase_order_lines')

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'))
    debit = db.Column(db.Float)
    credit = db.Column(db.Float)
    note = db.Column(db.String)
    purchase_event_id = db.Column(db.Integer, db.ForeignKey('purchase_event.id'))
    purchase_event = db.relationship('PurchaseEvent', back_populates='payments')

class DeliveryOrder(db.Model):
    __tablename__ = 'delivery_order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    driver = db.Column(db.String)
    vehicle_number = db.Column(db.String)
    purchase_event_id = db.Column(db.Integer, db.ForeignKey('purchase_event.id'))
    purchase_order_lines = db.relationship('PurchaseOrderLine', back_populates='delivery_order', lazy='dynamic')


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_order_odoo.id'))
    purchase_order = db.relationship('PurchaseOrderOdoo', foreign_keys=[purchase_order_id], backref=db.backref('transactions', lazy=True))
    station = db.Column(db.String, default="default")
    purchase_event_id = db.Column(db.Integer, db.ForeignKey('purchase_event.id'))
    purchase_event = db.relationship('PurchaseEvent', foreign_keys=[purchase_event_id], backref=db.backref('transactions', lazy=True))
    farmer_id = db.Column(db.Integer, db.ForeignKey('nfcapp_farmer_odoo.id'))
    farmer = db.relationship('NfcappFarmerOdoo', foreign_keys=[farmer_id], backref=db.backref('transactions', lazy=True))
    # item_code_id = db.Column(db.Integer, db.ForeignKey('product_odoo.id'))
    # item_code = db.Column(db.Integer, db.ForeignKey('product_odoo.id'))
    price_unit = db.Column(db.Float, default=100000)
    qty = db.Column(db.Float, default=100)
    subtotal = db.Column(db.Float)

    def __init__(self, purchase_order_id, purchase_event_id, farmer_id, price_unit, qty):
        self.purchase_order_id = purchase_order_id
        self.purchase_event_id = purchase_event_id
        self.farmer_id = farmer_id
        self.price_unit = price_unit
        self.qty =  qty
        self.subtotal = price_unit * qty

    def __repr__(self):
        return f'<Transaction {self.id}>'


class UserLogging(db.Model):
    __tablename__ = 'user_logging'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    session = db.Column(db.String(120))
    message = db.Column(db.String)
    device = db.Column(db.String)
    mac_address = db.Column(db.String)
    ip_address_local = db.Column(db.String)
    ip_address_external = db.Column(db.String)
    date = db.Column(db.DateTime)



















