from flask import redirect, Blueprint, render_template, request, flash, jsonify, url_for, session
import requests
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from . import users

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    return render_template('home.html', user=current_user)

@views.route('/new_playlist', methods=['GET', 'POST'])
@login_required
def new_playlist():
    
    now = datetime.now()
    month_name = now.strftime('%B')
    month = now.month
    year = now.year
    
    name = f'monthlyWrapped {month}/{year}'
    description = f'{current_user.username}\'s top 100 songs in {month_name} {year}'

    current_user.create_new_monthly_wrapped(name, description)

    return redirect(url_for('views.tracks'))

@views.route('/about')
@login_required
def about():
    return render_template('about.html')

@views.route('/tracks')
@login_required
def tracks():
    if 'access_token' not in session:
        return redirect(url_for('auth.login'))
    return render_template('tracks.html', user=current_user)