from flask import redirect, Blueprint, render_template, request, flash, jsonify, url_for, session
import requests
from flask_login import login_required, current_user
from . import db
from datetime import datetime
from .spotify_constants import AUTH_URL, REDIRECT_URI, CLIENT_ID, CLIENT_SECRET, TOKEN_URL


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # if request.method == 'POST':
    #     note = request.form.get('note')

    #     if len(note) < 1:
    #         flash('Note is too short', category='error')
    #     else:
    #         current_time = datetime.now()
    #         new_note = Note(data=note, date=current_time,
    #                         user_id=current_user.id)
    #         db.session.add(new_note)
    #         db.session.commit()
    #         flash('Note added', category='success')

    return render_template("home.html", user=current_user)


@views.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    return jsonify({})


# @views.route('/login', methods=['GET', 'POST'])
# def login():
#     """
#     Redirect to Spotify authorization page
#     """
#     return redirect(AUTH_URL)
