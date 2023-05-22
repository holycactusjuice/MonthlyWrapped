from flask import redirect, Blueprint, render_template, request, flash, jsonify, url_for, session
import requests
from flask_login import login_required, current_user
from . import users


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    else:
        return render_template('home.html', user=current_user)


@views.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    current_user.update_listen_data()
    return redirect(url_for('views.home'))


@views.route('/new_playlist', methods=['GET', 'POST'])
@login_required
def new_playlist():
    name = 'wrapped test'
    description = 'test'

    current_user.create_new_monthly_wrapped(name, description)

    return redirect(url_for('views.home'))


@views.route('/data', methods=['GET', 'POST'])
@login_required
def data():
    return render_template('data.html')


@views.route('/email_data', methods=['GET', 'POST'])
@login_required
def email_data():
    current_user.email_listen_data()
    return redirect(url_for('views.data'))
