import requests
import json
import datetime
import base64
import string
import secrets
from urllib.parse import urlencode
from flask import redirect

from .misc import played_at_unix
from .constants import *


# def get_access_token(client_id, client_secret):
#     """
#     Get access token for the given client_id and client_secret
#     """

#     auth_string = client_id + ':' + client_secret
#     auth_bytes = auth_string.encode('utf-8')
#     auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

#     url = TOKEN_URL
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'Authorization': 'Basic' + auth_base64
#     }


def user_auth(client_id, response_type, redirect_uri, scopes):  # add state parameter
    """
    Requests user authorization
    """

    state = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
    )

    data = {
        'response_type': response_type,
        'client_id': client_id,
        'scope': " ".join(scopes),
        'redirect_uri': redirect_uri,
        'state': state
    }

    auth_url = 'https://accounts.spotify.com/authorize?' + urlencode(data)

    return redirect(auth_url)


def get_account_info(access_token):
    response = requests.get(
        endpoints['get_user'],
        headers={
            "Authorization": "Bearer " + access_token,
        }
    )
    return response.json()


def get_track_data(track):
    """
    Gets the track data given a track json
    """
    # track_id = track['track']['id']
    title = track['track']['name']
    artists = [artist["name"]
               for artist in track["track"]["artists"]]
    album = track["track"]["album"]["name"]
    album_art_url = track["track"]["album"]["images"][0]["url"]
    length = int(track['track']['duration_ms'] / 1000)

    track_data = {
        # "track_id": track_id,
        'title': title,
        'artists': artists,
        'album': album,
        'album_art_url': album_art_url,
        'length': length,
    }

    return track_data


def get_recent_tracks(access_token, limit):
    """
    Gets user's recent tracks from Spotify API and returns the following information:
    - track name
    - artist name(s)
    - album
    - album art url
    - time played at
    - duration played for

    Args:
        access_token (str): Spotify access token
        limit (int): number of tracks to return

    Returns:
        tracks (dict): track_id : track_info
    """
    url = endpoints['get_recently_played']
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "before": int(TIME),
        "limit": limit
    }
    reponse = requests.get(
        url=url,
        headers=headers,
        params=params
    )

    resp_json = reponse.json()

    recent_tracks = resp_json['items']

    # reverse list since the last played track is given first
    recent_tracks.reverse()

    tracks = {}

    for i, track in enumerate(recent_tracks):
        # print(track)

        track_id = track['track']['id']

        if track_id not in tracks:

            track_data = get_track_data(track)
            tracks[track_id] = track_data

        # get the time this track ended in unix timestamp
        # time_string is the format: 2023-02-12T17:18:28.679Z
        played_at = played_at_unix(track['played_at'])

        # if not first track in list and this listen has not been recorded
        if i != 0 and played_at not in tracks[track_id]["listen_data"].keys():

            track_length = int(tracks[track_id]['track_length'])

            # get the time the last track ended in unix timestamp
            last_track = recent_tracks[i - 1]
            last_played_at = played_at_unix(last_track['played_at'])

            # duration is the difference between when the last track ended (when this track started) and when this track ended
            duration = played_at - last_played_at

            # duration may be greater than track length if:
            #   - the user took a break before playing the track
            #   - the user paused the track
            #   - this is the first song in the session
            # so if duration > track_length, make duration = track_length
            duration = min(duration, track_length)

            # add this listen to the user's data
            tracks[track_id]["listen_data"][played_at] = duration

    return tracks
