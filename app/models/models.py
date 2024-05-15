from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db
from app.models.models_odoo import ResUserOdoo, ProductOdoo, PurchaseOrderOdoo, PurchaseOrderLineOdoo, NfcappFarmerOdoo


session = db.session


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Farmer(db.Model):
    __tablename__ = 'farmer'
    id = db.Column(db.Integer, primary_key=True)
    farmer_name = db.Column(db.String(128))
    farmer_code = db.Column(db.String(64))
    products = db.relationship('Product', back_populates='farmer', lazy='dynamic')

    def __repr__(self):
        return '<Farmer %r>' % self.farmer_name

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(64))
    product_name = db.Column(db.String(128))
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))
    farmer = db.relationship('Farmer', back_populates='products')
    product_odoo_id = db.Column(db.Integer, db.ForeignKey('product_odoo.id'))


class PurchaseEvent(db.Model):
    __tablename__ = 'purchase_event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    fund = db.Column(db.Float, default=100000)
    ics = db.Column(db.String)
    purchaser = db.Column(db.Integer, db.ForeignKey('res_user_odoo.id'))
    cashier = db.Column(db.Integer, db.ForeignKey('res_user_odoo.id'))
    ap_name = db.Column(db.String)
    ip_address = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False)
    purchase_order_odoo_id = db.Column(db.Integer, db.ForeignKey('purchase_order_odoo.id'))
    purchase_orders = db.relationship('PurchaseOrder', back_populates='purchase_event', lazy='dynamic')
    payments = db.relationship('Payment', back_populates='purchase_event', lazy='dynamic')


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_order'
    id = db.Column(db.Integer, primary_key=True)
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

















