from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import requests
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from .constants import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_URL
import json
from urllib.parse import urlencode


from .misc import is_valid_email, build_state

auth = Blueprint('auth', __name__)


@auth.route('/')
@login_required
def home():
    return render_template('home.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@auth.route('/spotify-login', methods=['GET', 'POST'])
def spotify_login():
    response_type = 'code'
    scopes = ['user-read-private',
              'user-read-email', 'playlist-modify-private']
    response = requests.get(
        'https://accounts.spotify.com/authorize',
        params={
            'response_type': response_type,
            'client_id': CLIENT_ID,
            'scope': " ".join(scopes),
            'redirect_uri': REDIRECT_URI,
            'state': build_state()
        }
    )
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    j = json.loads(response.content)
    flash(j)
    return response
