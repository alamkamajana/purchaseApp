from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date
from . import db
import uuid
from sqlalchemy import LargeBinary
session = db.session
from sqlalchemy.orm import validates
from sqlalchemy import event
user_purchase_order_association = db.Table('user_purchase_order_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('purchase_order_odoo_id', db.Integer, db.ForeignKey('purchase_order_odoo.id'), primary_key=True)
)


def get_change_id():
    return str(uuid.uuid4())


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
    uniq_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    change_id = db.Column(db.String(36), default=get_change_id, onupdate=get_change_id)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    fund = db.Column(db.Float)
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
    note = db.Column(db.Text)
    date_stamp = db.Column(db.Date)
    money_entries = db.relationship('Money', backref='purchase_event', lazy='dynamic')

    @property
    def compute_balance(self):
        total_fund = sum(m.amount for m in self.money_entries)
        return total_fund

    @property
    def compute_money_out(self):
        money_out = 0
        for money in self.money_entries :
            if money.amount < 0 :
                money_out += money.amount
        return money_out

    @property
    def compute_money_in(self):
        money_in = 0
        for money in self.money_entries:
            if money.amount > 0:
                money_in += money.amount
        return money_in



class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_order'
    uniq_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    change_id = db.Column(db.String(36), default=get_change_id, onupdate=get_change_id)
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
    date = db.Column(db.Date)
    created = db.Column(db.DateTime)
    modified = db.Column(db.DateTime)
    create_uid = db.Column(db.Integer)
    write_uid = db.Column(db.Integer)
    money_entries = db.relationship('Money', backref='purchase_order', lazy='dynamic')
    signature = db.Column(db.LargeBinary)

    @property
    def compute_payment(self):
        total_payment = sum(m.amount for m in self.money_entries)
        return total_payment
    @property
    def amount_total(self):
        return sum(line.subtotal for line in self.purchase_order_lines)

    @property
    def compute_is_paid(self):
        calculation = self.amount_total + self.compute_payment
        payment_positive = abs(self.compute_payment)
        print("Hasil is paid")
        if payment_positive >= self.amount_total and int(self.compute_payment) != 0 :
            
            return True
        elif int(calculation) > 0 :
            
            return False
        else :
            
            return False


class PurchaseOrderLine(db.Model):
    __tablename__ = 'purchase_order_line'
    uniq_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    change_id = db.Column(db.String(36), default=get_change_id, onupdate=get_change_id)
    id = db.Column(db.Integer, primary_key=True)
    product_odoo_id = db.Column(db.Integer, db.ForeignKey('product_odoo.id'))
    nfcapp_commodity_item_odoo_id = db.Column(db.Integer, db.ForeignKey('nfcapp_commodity_item_odoo.id'))
    nfcapp_commodity_item_odoo = db.relationship('NfcappCommodityItemOdoo')
    qty = db.Column(db.Float)
    unit_price = db.Column(db.Float)
    barcode = db.Column(db.String)
    commodity_name = db.Column(db.String)
    variant = db.Column(db.String)
    is_organic = db.Column(db.Boolean)
    is_ra_cert = db.Column(db.Boolean)
    color_name = db.Column(db.String)
    color_hex = db.Column(db.String)
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
    note = db.Column(db.Text)

class Payment(db.Model):
    __tablename__ = 'payment'
    uniq_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    change_id = db.Column(db.String(36), default=get_change_id, onupdate=get_change_id)
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
    uniq_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    change_id = db.Column(db.String(36), default=get_change_id, onupdate=get_change_id)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    driver = db.Column(db.String)
    vehicle_number = db.Column(db.String)
    purchase_event_id = db.Column(db.Integer, db.ForeignKey('purchase_event.id'))
    purchase_order_lines = db.relationship('PurchaseOrderLine', back_populates='delivery_order', lazy='dynamic')
    sent_date = db.Column(db.DateTime)
    received_date = db.Column(db.DateTime)
    origin = db.Column(db.String)
    destination = db.Column(db.String)
    note = db.Column(db.Text)
    status = db.Column(db.String(64))
    created = db.Column(db.DateTime)
    modified = db.Column(db.DateTime)
    create_uid = db.Column(db.Integer)
    write_uid = db.Column(db.Integer)

    @property
    def compute_total_qty(self):
        total_qty = sum(m.qty for m in self.purchase_order_lines)
        return total_qty




class Money(db.Model):
    __tablename__ = 'money'
    uniq_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    change_id = db.Column(db.String(36), default=get_change_id, onupdate=get_change_id)
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String)
    purchase_event_id = db.Column(db.Integer, db.ForeignKey('purchase_event.id'))
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'))
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'))
    amount = db.Column(db.Float)
    note = db.Column(db.Text)
    created = db.Column(db.DateTime)
    modified = db.Column(db.DateTime)
    create_uid = db.Column(db.Integer)
    write_uid = db.Column(db.Integer)


class Expense(db.Model):
    __tablename__ = 'expense'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    purchase_event_id = db.Column(db.Integer, db.ForeignKey('purchase_event.id'))
    amount = db.Column(db.Float)
    note = db.Column(db.Text)
    created = db.Column(db.DateTime)
    modified = db.Column(db.DateTime)
    create_uid = db.Column(db.Integer)
    write_uid = db.Column(db.Integer)
    image = db.Column(LargeBinary)
    money_entries = db.relationship('Money', backref='expense', lazy='dynamic')
    @property
    def compute_payment(self):
        total_payment = sum(m.amount for m in self.money_entries)
        return total_payment

    @property
    def payment_debt(self):
        total_payment = sum(m.amount for m in self.money_entries)
        debt = self.amount + total_payment
        return debt

