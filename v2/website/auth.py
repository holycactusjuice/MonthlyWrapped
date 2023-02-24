from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import requests
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from .constants import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_URL, CLIENT_CREDS_B64, TOKEN_URL
import json
from urllib.parse import urlencode
import base64
from .spotify import get_user_id

from .misc import is_valid_email, build_state

auth = Blueprint('auth', __name__)


@auth.route('/')
@login_required
def home():
    if 'access_token' not in session:
        return redirect(url_for('login'))
    # Use the access_token to make requests to the Spotify API
    # For example:
    headers = {'Authorization': 'Bearer ' + session['access_token']}
    response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    return response.text


@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@auth.route('/spotify-login', methods=['GET', 'POST'])
def spotify_login():
    response_type = 'code'
    scopes = ["playlist-modify-public", "playlist-modify-private", "ugc-image-upload", "user-read-recently-played", "user-read-private", "user-read-email",]
    auth_params = {
        'response_type': response_type,
        'client_id': CLIENT_ID,
        'scope': " ".join(scopes),
        'redirect_uri': REDIRECT_URI,
        'state': build_state()
    }

    return redirect(AUTH_URL + "?" + urlencode(auth_params))

    
@auth.route('/callback')
def callback():
    auth_token = request.args['code']
    data = {
        'grant_type': 'authorization_code',
        'code': auth_token,
        'redirect_uri': REDIRECT_URI,
    }
    headers = {'Authorization': 'Basic ' + CLIENT_CREDS_B64, 'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(TOKEN_URL, params=data, headers=headers)
    if response.status_code == 200:
        response_data = json.loads(response.text)

        access_token = response_data["access_token"]
        refresh_token = response_data["refresh_token"]
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token

        user_id = get_user_id(access_token)
        flash(user_id)


        return redirect(url_for('auth.home'))
    else:
        return redirect(url_for('auth.login'))
        