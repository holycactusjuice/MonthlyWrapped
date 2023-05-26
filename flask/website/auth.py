from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import requests
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
import json
from urllib.parse import urlencode
from bson import ObjectId
import urllib

from . import users
from .misc import build_state
from .constants import CLIENT_ID, REDIRECT_URI, AUTH_URL, CLIENT_CREDS_B64, TOKEN_URL, SCOPES

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@auth.route('/spotify-login', methods=['GET', 'POST'])
def spotify_login():
    session.clear()
    response_type = 'code'
    scopes = SCOPES
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
    params = {
        'grant_type': 'authorization_code',
        'code': auth_token,
        'redirect_uri': REDIRECT_URI,
    }
    headers = {
        'Authorization': 'Basic ' + CLIENT_CREDS_B64,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(TOKEN_URL, params=params, headers=headers)

    if response.status_code == 200:
        response_data = json.loads(response.text)

        access_token = response_data["access_token"]
        refresh_token = response_data["refresh_token"]
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token

        info = User.get_account_info(access_token)

        username = info['id']
        user_doc = users.find_one({"username": username})

        # if user not found, create new user and add to database
        if user_doc is None:
            email = info['email']
            display_name = info['display_name']
            pfp = info['images'][0]['url']

            user = User(_id=ObjectId(), username=username, email=email,
                        display_name=display_name, pfp=pfp, access_token=access_token, refresh_token=refresh_token)

            users.insert_one(user.dict())
            flash('user added to database')
        user = User.from_username(username)  # loads with email
        login_user(user, remember=True)
        return redirect(url_for('views.home'))
    else:
        return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    # Clear the session and redirect the user to the Spotify logout URL
    logout_user()
    session.clear()

    logout_url = 'https://accounts.spotify.com/en/logout'

    return redirect(logout_url)
