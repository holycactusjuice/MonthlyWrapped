from flask import redirect, Blueprint, render_template, request, flash, jsonify, url_for, session
import requests
from flask_login import login_required, current_user
from . import db

from .spotify import get_recent_tracks

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
    access_token = session.get('access_token')
    recent_tracks = get_recent_tracks(access_token, 10)
    for track in recent_tracks:
        flash(track.title)
    return render_template('update.html', user=current_user)
