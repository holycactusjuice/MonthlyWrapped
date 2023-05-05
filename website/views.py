from flask import redirect, Blueprint, render_template, request, flash, jsonify, url_for, session
import requests
from flask_login import login_required, current_user
from . import users

from .spotify import get_recent_tracks
from .mongo import get_user_document

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
