from datetime import datetime, date
import datetime as dt

import flask.json
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, Response, jsonify
from dotenv import load_dotenv
import os
import aiohttp
import asyncio
import ssl
import requests
from app.models.models import User
from app.models.models import PurchaseEvent, PurchaseOrder, PurchaseOrderLine, Payment, DeliveryOrder, Money
from app.models.models_odoo import NfcappFarmerOdoo, ProductOdoo
from app.models.db import db
from .auth import login_required
import json
import logging
import base64


load_dotenv()
bp = Blueprint('upload_nfcpurchase', __name__, url_prefix='/nfcpurchase')
ODOO_BASE_URL = os.getenv('BASE_URL_ODOO')
TOKEN = os.getenv('TOKEN')


MODEL_NAMES = {
    "PurchaseEvent": PurchaseEvent,
    "PurchaseOrder": PurchaseOrder,
    "PurchaseOrderLine": PurchaseOrderLine,
    "Payment": Payment,
    "DeliveryOrder": DeliveryOrder,
    "Money": Money,
}


def serialize_model(model_instance):
    """
    Serialize a SQLAlchemy model instance to a dictionary.
    """
    uniq_id_upload_columns = {
        "purchase_event": "purchase_event_uniq_id",
        "purchase_order": "purchase_order_uniq_id",
        "delivery_order": "delivery_order_uniq_id",
        "purchase_order_odoo": "purchase_order_odoo_true_id",
        "farmer_id": "farmer_odoo_true_id",
        "product_odoo_id": "product_odoo_true_id",
    }
    serialized_data = {}
    for column in model_instance.__table__.columns:
        if column.name == 'signature':
            value = getattr(model_instance, column.name)
            if value is not None:
                value = base64.b64encode(value).decode('utf-8')  # Convert binary data to base64 string
        else:
            value = getattr(model_instance, column.name)
            if isinstance(value, (datetime, date)):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
        serialized_data[column.name] = value

    for column_name, uniq_id_name in uniq_id_upload_columns.items():
        if hasattr(model_instance, column_name):
            if column_name == "farmer_id":
                farmer_id = getattr(model_instance, "farmer_id")
                if farmer_id:
                    farmer = NfcappFarmerOdoo.query.get(farmer_id)
                    serialized_data["farmer_odoo_true_id"] = farmer.odoo_id
            elif column_name == "product_odoo_id":
                product_odoo_id = getattr(model_instance, "product_odoo_id")
                if product_odoo_id:
                    product_odoo = ProductOdoo.query.get(product_odoo_id)
                    serialized_data["product_odoo_true_id"] = product_odoo.odoo_id
            elif hasattr(model_instance, uniq_id_name):
                serialized_data[uniq_id_name] = getattr(model_instance, uniq_id_name)

    return serialized_data


def get_query_data(flask_model, uniq_ids):
    query = flask_model.query.filter(flask_model.uniq_id.in_(uniq_ids)).all()
    return [serialize_model(record) for record in query]


async def async_post_data(session, url, data):
    headers = {"Content-Type": "application/json"}
    async with session.post(url, json=data, headers=headers) as response:
        response.raise_for_status()
        return await response.json()


async def async_upload_ids(session, nfcpurchase):
    model = MODEL_NAMES[nfcpurchase]
    nfcpurchase_ids = model.query.with_entities(model.uniq_id, model.change_id).all()
    nfcpurchase_dict = [{'uniq_id': item[0], 'change_id': item[1]} for item in nfcpurchase_ids]
    data = {"model": nfcpurchase, "token": TOKEN, "nfcpurchase_dict": nfcpurchase_dict}
    url = f"{ODOO_BASE_URL}/nfcpurchase/upload/all/get_ids/"

    try:
        response = await async_post_data(session, url, data)
        return response
    except aiohttp.ClientError as e:
        print(e)
        return False


async def async_upload_all():
    url_create = f"{ODOO_BASE_URL}/nfcpurchase/upload/all/create/"
    url_update = f"{ODOO_BASE_URL}/nfcpurchase/upload/all/update/"

    json_responses = []

    async with aiohttp.ClientSession() as session:
        for model_name, flask_model in MODEL_NAMES.items():
            get_ids_list = await async_upload_ids(session, model_name)
            if not get_ids_list:
                continue

            if "result" not in get_ids_list:
                continue

            result = json.loads(get_ids_list["result"])
            to_create_list, to_update_list = result["to_create_list"], result["to_update_list"]
            json_responses.append(result)

            if to_create_list:
                query_create_data = get_query_data(flask_model, to_create_list)
                create_data = {"model": model_name, "token": TOKEN, "data": query_create_data}
                await async_post_data(session, url_create, create_data)

            if to_update_list:
                query_update_data = get_query_data(flask_model, to_update_list)
                update_data = {"model": model_name, "token": TOKEN, "data": query_update_data}
                await async_post_data(session, url_update, update_data)

    return json_responses


@bp.route("/upload/all/", methods=["GET"])
@login_required
def upload_all():
    try:
        json_responses = asyncio.run(async_upload_all())
        return jsonify(json_responses)
    except Exception as e:
        print(e)
        return str(e), 500


@bp.route("/upload/check-update-by-id/", methods=["GET"])
@login_required
def check_update():
    check_id = request.args.get("check_id")
    model_name = request.args.get("model")
    model = MODEL_NAMES.get(model_name)
    query_model = model.query.get(int(check_id))

    if query_model:
        url = f"{ODOO_BASE_URL}/nfcpurchase/upload/check_update/"
        data = {"token": TOKEN, "model": model_name, "uniq_id": query_model.uniq_id, "change_id": query_model.change_id}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=data, headers=headers)
        # response = post_data(url, data)

        if response.status_code == requests.codes.ok:
            try:
                json_response = response.json()
                results = json_response["result"]
                return jsonify(results), 200
            except (ValueError, KeyError):
                return jsonify({"error": "Invalid response format from odoo"}), 500
        else:
            return jsonify({"error": "Failed to get a valid response from odoo"}), response.status_code


@bp.route("/upload/update/", methods=["POST"])
@login_required
def update_with_update_type():
    update_id = request.form.get("update_id")
    model_name = request.form.get("model")
    update_type = request.form.get("update_type")  # update or create
    model = MODEL_NAMES[model_name]
    query_model = model.query.get(int(update_id))

    if query_model:
        url = f"{ODOO_BASE_URL}/nfcpurchase/upload/all/{update_type}/"
        query_data = [serialize_model(query_model)]
        data = {"model": model_name, "token": TOKEN, "data": query_data}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=data, headers=headers)
        # response = post_data(url, data)
        json_response = response.json()
        return jsonify(json_response["result"])

