from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import requests
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
import json
from urllib.parse import urlencode
from bson import ObjectId

from . import db, users
from .spotify import get_account_info
from .misc import build_state
from .constants import CLIENT_ID, REDIRECT_URI, AUTH_URL, CLIENT_CREDS_B64, TOKEN_URL

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@auth.route('/spotify-login', methods=['GET', 'POST'])
def spotify_login():
    response_type = 'code'
    scopes = ["playlist-modify-public", "playlist-modify-private", "ugc-image-upload",
              "user-read-recently-played", "user-read-private", "user-read-email",]
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
    flash('status ', response.status_code)
    if response.status_code == 200:
        response_data = json.loads(response.text)

        access_token = response_data["access_token"]
        refresh_token = response_data["refresh_token"]
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token

        info = get_account_info(session.get('access_token'))
        email = info['email']

        user = users.find_one({"email": email})

        # if user not found, create new user and add to database
        if user is None:
            display_name = info['display_name']
            username = info['id']
            pfp = info['images'][0]['url']

            user = User(_id=ObjectId(), username=username, email=email,
                        display_name=display_name, pfp=pfp)

            users.insert_one(user.dict())
            flash('user added to database')
        user = User.from_email(email)  # loads with email
        flash(user.dict())
        login_user(user, remember=True)
        return redirect(url_for('views.home'))
    else:
        return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    # Clear the session and redirect the user to the Spotify logout URL
    session.clear()
    return redirect('https://www.spotify.com/logout/')
    return direct(url_for('auth.login'))
