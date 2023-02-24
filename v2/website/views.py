from flask import redirect, Blueprint, render_template, request, flash, jsonify, url_for, session
import requests
from flask_login import login_required, current_user
from . import db
from spotify import get_user_id

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'GET':
        access_token = session.get('access_token')
        user_id = get_user_id(access_token)
        flash(user_id)
        return render_template('home.html')
    else:
        return render_template('login.html')

