from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import requests
import json
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import re
from .spotify_constants import *
from .spotify_api_test import get_user_id

auth = Blueprint('auth', __name__)


def is_valid_email(email):
    # Define the regular expression pattern to match a valid email address
    pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    # Use the pattern to check if the email matches the regular expression
    if pattern.match(email):
        return True
    return False


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # return redirect(AUTH_URL)
    return render_template('login.html', user=current_user)


@auth.route('/login-spotify', methods=['GET', 'POST'])
def login_spotify():
    return redirect(AUTH_URL)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/callback', methods=['GET', 'POST'])
def callback():
    """Exchange authorization code for access token and refresh token"""
    code = request.args.get('code')
    if code is None:
        # Handle error case
        flash('No code provided')

        return redirect(url_for('auth.login'))
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(TOKEN_URL, data=data, headers=headers)
    if response.status_code == 200:
        token_data = response.json()
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data['refresh_token']
        # return redirect(url_for('views.home'))
        user = current_user
        flash(get_user_id())

        login_user(user, remember=True)
        flash(user.is_authenticated)

        if user.is_authenticated:
            flash('Successfully logged in')
        return render_template("home.html", user=user)
    else:
        # Handle error case
        return redirect(url_for('auth.login'))


# @auth.route('/sign-up', methods=['GET', 'POST'])
# def sign_up():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         username = request.form.get('username')
#         password1 = request.form.get('password1')
#         password2 = request.form.get('password2')

#         user = User.query.filter_by(email=email).first()

#         if user:
#             flash('An account with that email already exists', category='error')
#         elif not is_valid_email(email):
#             flash('Please enter a valid email address.', category='error')
#         elif password1 != password2:
#             flash('Passwords do not match.', category='error')
#         elif len(password1) < 6:
#             flash('Password must be at least 6 characters.', category='error')
#         else:
#             new_user = User(email=email, username=username, password=generate_password_hash(
#                 password1, method='sha256'))
#             db.session.add(new_user)
#             db.session.commit()

#             login_user(new_user, remember=True)

#             flash('Account created!', category='success')

#             return redirect(url_for('views.home'))

#     return render_template('sign_up.html', user=current_user)
