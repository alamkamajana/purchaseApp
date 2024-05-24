from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db

session = db.session

user_purchase_order_association = db.Table('user_purchase_order_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('purchase_order_odoo_id', db.Integer, db.ForeignKey('purchase_order_odoo.id'), primary_key=True)
)


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
    created = db.Column(db.DateTime)

    def __repr__(self):
        return '<User %r>' % self.username

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
    created = db.Column(db.DateTime)
    date = db.Column(db.DateTime)

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
    created_at = db.Column(db.DateTime)
    purchase_order_odoo_id = db.Column(db.Integer, db.ForeignKey('purchase_order_odoo.id'))
    purchase_order_odoo = db.relationship('PurchaseOrderOdoo', foreign_keys=[purchase_order_odoo_id], backref=db.backref('purchase_events', lazy=True))
    purchase_orders = db.relationship('PurchaseOrder', back_populates='purchase_event', lazy='dynamic')
    payments = db.relationship('Payment', back_populates='purchase_event', lazy='dynamic')
    created = db.Column(db.DateTime)
    modified = db.Column(db.DateTime)
    create_uid = db.Column(db.Integer)
    write_uid = db.Column(db.Integer)

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    receipt_number = db.Column(db.String(64))
    purchase_order_lines = db.relationship('PurchaseOrderLine', back_populates='purchase_order', lazy='dynamic')
    farmer_id = db.Column(db.Integer, db.ForeignKey('nfcapp_farmer_odoo.id'))
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))
    status = db.Column(db.String(64))
    purchase_event_id = db.Column(db.Integer, db.ForeignKey('purchase_event.id'))
    is_paid = db.Column(db.Boolean)
    purchase_event = db.relationship('PurchaseEvent', back_populates='purchase_orders')
    created = db.Column(db.DateTime)
    modified = db.Column(db.DateTime)
    create_uid = db.Column(db.Integer)
    write_uid = db.Column(db.Integer)

    @property
    def amount_total(self):
        return sum(line.subtotal for line in self.purchase_order_lines)

class PurchaseOrderLine(db.Model):
    __tablename__ = 'purchase_order_line'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product_odoo.id'))
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
    created = db.Column(db.DateTime)
    modified = db.Column(db.DateTime)
    create_uid = db.Column(db.Integer)
    write_uid = db.Column(db.Integer)

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'))
    debit = db.Column(db.Float)
    credit = db.Column(db.Float)
    note = db.Column(db.String)
    purchase_event_id = db.Column(db.Integer, db.ForeignKey('purchase_event.id'))
    purchase_event = db.relationship('PurchaseEvent', back_populates='payments')
    created = db.Column(db.DateTime)
    modified = db.Column(db.DateTime)
    create_uid = db.Column(db.Integer)
    write_uid = db.Column(db.Integer)

class DeliveryOrder(db.Model):
    __tablename__ = 'delivery_order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    driver = db.Column(db.String)
    vehicle_number = db.Column(db.String)
    purchase_event_id = db.Column(db.Integer, db.ForeignKey('purchase_event.id'))
    purchase_order_lines = db.relationship('PurchaseOrderLine', back_populates='delivery_order', lazy='dynamic')
    created = db.Column(db.DateTime)
    modified = db.Column(db.DateTime)
    create_uid = db.Column(db.Integer)
    write_uid = db.Column(db.Integer)

