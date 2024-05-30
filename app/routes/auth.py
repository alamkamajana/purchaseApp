from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
from flask_login import login_user, current_user
from app.models.models import User, UserSession
from dotenv import load_dotenv
import os
import requests
from app.models.db import db
import requests
from functools import wraps
import socket
import requests
from datetime import datetime
import os
import uuid
import re

load_dotenv()
bp = Blueprint('auth', __name__,)
odoo_base_url = os.getenv('BASE_URL_ODOO')
odoo_db = os.getenv('ODOO_DATABASE')
token = os.getenv('TOKEN')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'username' in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('routes.auth.login'))
        elif 'username' in session :
            username = session['username']
            user = User.query.filter_by(username=username).first()
            if not user :
                flash('Please log in to access this page.', 'danger')
                return redirect(url_for('routes.auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get client IP address
        client_ip = request.remote_addr or 'Unknown'
        # Get client device name (if available)
        client_device_name = request.user_agent.platform or 'Unknown'
        # Get client MAC address (if available)
        client_mac_address = request.access_route[0] or 'Unknown'

        # Handle login logic here
        username = request.form['username']
        password = request.form['password']
        login_endpoint = f"{odoo_base_url}/api/purchase/login"
        login_data = {
            'database': odoo_db,
            'username': username,
            'password': password
        }
        login_session = requests.Session()
        login = login_session.post(login_endpoint, json=login_data)
        # Authenticate the user against the external application
        # user_session = login.cookies.get_dict()
        login_data = login.json()
        # print(password)
        if login_data['result']['status'] == 200:
            data_login = login_data['result']
            print(data_login)
            user = User.query.filter_by(username=data_login['name'] if data_login['name'] else None).first()
            # session['username'] = data_login['name']
            datetime_now = datetime.today()

            user_session_data = UserSession(username=data_login['name'] if data_login['name'] else None,email=data_login['email'], session=data_login['token'],action='login',device=client_device_name,ip_address_external=client_ip,date=datetime_now,mac_address=client_mac_address)
            db.session.add(user_session_data)
            db.session.commit()

            if not user:
                user = User(username=data_login['name'],email=data_login['email'], session=data_login['token'],user_odoo_id=data_login['user_odoo_id'])
                db.session.add(user)
                db.session.commit()
            # user = User(username=data_login['name'],email=data_login['email'], session=data_login['token'])
            session['username'] = data_login['name']
            session['email'] = data_login['email']
            session['token'] = data_login['token']
            session['user_odoo_id'] = data_login['user_odoo_id']
            # print(session['user_odoo_id'])
            # login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('routes.auth.main_page'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('/auth/login.html')


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    # Get client IP address
    client_ip = request.remote_addr or 'Unknown'
    # Get client device name (if available)
    client_device_name = request.user_agent.platform or 'Unknown'
    # Get client MAC address (if available)
    client_mac_address = request.access_route[0] or 'Unknown'
    datetime_now = datetime.today()

    user_session_data = UserSession(username=session['username'], email=session['email'], session=session['token'],
                                    action='logout', device=client_device_name,
                                    ip_address_external=client_ip, date=datetime_now, mac_address=client_mac_address)
    db.session.add(user_session_data)
    db.session.commit()

    session.pop('username', None)
    session.pop('email', None)
    session.pop('token', None)
    session.pop('user_odoo_id', None)
    flash('You Are Logged Out !', 'info')
    return redirect(url_for('routes.auth.login'))


@bp.route('/')
@login_required
def main_page():
    try :
        return redirect("/server/purchase-event")
    except Exception as e:
        print(e)
        return {"message": str(e), "status":400}