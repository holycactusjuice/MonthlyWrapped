from flask import redirect, Blueprint, render_template, request, flash, jsonify, url_for, session
import requests
from flask_login import login_required, current_user
from . import users

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
    recent_tracks = get_recent_tracks(access_token, 50)

    for track in recent_tracks:
        query = {'username': current_user.username,
                 'listen_data.track_id': track.track_id}

        # update the following fields:
        #   - last_listen
        #   - listen_count
        #   - time_listened
        result = users.find_one(
            {
                'username': current_user.username,
                'listen_data': {'$elemMatch': {'track_id': track.track_id}}
            },
            {'listen_data.$': 1}
        )
        if result:
            # check if this listen has already been recorded
            # if last_listen > the track to be added's last_listen, then add it
            if track.last_listen > result['listen_data'][0]['last_listen']:
                update = {
                    '$set': {
                        'listen_data.$.last_listen': track.last_listen,
                    },
                    '$inc': {
                        'listen_data.$.listen_count': track.listen_count,
                        'listen_data.$.time_listened': track.time_listened
                    }
                }
                users.update_one(query, update)
        else:
            users.update_one(
                {'username': current_user.username},
                {'$push': {'listen_data': track.__dict__}}
            )

    current_user.update_user()

    return redirect(url_for('views.home'))
