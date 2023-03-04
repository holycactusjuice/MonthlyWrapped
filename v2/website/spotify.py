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
class Track():
    def __init__(self, track_id, title, artists, album, album_art_url, length, last_listen=-1, listen_count=0, time_listened=0):
        self.track_id = track_id
        self.title = title
        self.artists = artists
        self.album = album
        self.album_art_url = album_art_url
        self.length = length
        self.last_listen = last_listen
        self.listen_count = listen_count
        self.time_listened = time_listened


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
    url = endpoints['get_user']
    headers = {
        "Authorization": "Bearer " + access_token,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.get(
        url=url, headers=headers
    )
    print('--------------------------------')
    print(response.json())
    print('--------------------------------')
    return response.json()


def get_track_data(track_json):
    """
    Gets the track data given a track json

    Args:
        track_json (dict): track json received from Spotify API
    Returns:
        track (Track): Track object with track data
    """
    track_id = track_json['track']['id']
    title = track_json['track']['name']
    artists = [artist["name"]
               for artist in track_json["track"]["artists"]]
    album = track_json["track"]["album"]["name"]
    album_art_url = track_json["track"]["album"]["images"][0]["url"]
    length = int(track_json['track']['duration_ms'] / 1000)

    track = Track(track_id, title, artists, album, album_art_url, length)

    return track


def get_recent_tracks(access_token, limit=50):
    """
    Gets user's recent tracks from Spotify API and returns a list of Track objects in the following format:
    [
        {
            'track_id' (str): 'track1',
            'title' (str): 'track1_title',
            'artists' (list): ['artist1', 'artist2'],
            'album' (str): 'album',
            'album_art_url' (str): 'j3208qprum1pr82',
            'length' (int): 123,
            'last_listen' (int): 1234567890,
            'listen_count' (int): 123,
            'time_listened' (int): 123456,
        },
        {
            'track_id' (str): 'track2',
            ...
        }
    ]
    Args:
        access_token (str): Spotify access token
        limit (int): number of tracks to return

    Returns:
        tracks (list): list of Track objects
    """

    # kwargs for GET request
    url = endpoints['get_recently_played']
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "before": int(TIME),  # must be int
        "limit": limit
    }

    # send GET request to Spotify's get recently played endpoint
    response = requests.get(
        url=url,
        headers=headers,
        params=params
    )

    # if the response gives a 401 error, the access token has expired
    # return -1 to indicate this
    if response.status_code == 401:
        return -1

    # get json from response object
    resp_json = response.json()

    recent_tracks = resp_json['items']

    # reverse list since Spotify API gives last played track first
    recent_tracks.reverse()

    tracks = []

    # iterate through each track json in recent_tracks to turn each one into a Track object
    for i, track_json in enumerate(recent_tracks):

        # we can't calculate listen time for the first track since there is no track before it
        # so skip the iteration if i == 0
        if i == 0:
            continue

        track = get_track_data(track_json)

        # add the track to tracks
        tracks.append(track)

        # with the index, the track can now be updated
        # update the following fields:
        #   - last_listen
        #   - listen_count
        #   - time_listened

        # updating last_listen

        # get the time this track ended
        played_at = played_at_unix(track_json['played_at'])
        track.last_listen = played_at

        # updating listen_count

        track.listen_count = 1

        # updating time_listened

        length = int(track.length)
        # get the time the last track ended in unix timestamp
        last_track = recent_tracks[i - 1]
        last_played_at = played_at_unix(last_track['played_at'])
        # time_listened is the difference between when the last track ended (when this track started) and when this track ended
        time_listened = played_at - last_played_at
        # time_listened may be greater than track length if:
        #   - the user took a break before playing the track
        #   - the user paused the track
        #   - this is the first song in the session
        # so if time_listened > track_length, make time_listened = track_length
        time_listened = min(time_listened, length)
        track.time_listened = time_listened

        tracks.append(track)

    return tracks


def swap_tokens(refresh_token):
    """
    Swaps the current refresh token for a new access token (and refresh token if the last one has expired)

    Args:
        refresh_token (str): old refresh token

    Returns:
        new_access_token (str): new access token
    """
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + CLIENT_CREDS_B64,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    params = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    response = requests.post(
        url=url, headers=headers, data=params
    )
    resp_json = response.json()

    new_access_token = resp_json['access_token']
    
    tokens = {
        'access_token': new_access_token
    }
    
    # Spotiy only gives a refresh token if the last one has expired
    # check if the response json has a refresh token and return
    if 'refresh_token' in resp_json:
        new_refresh_token = resp_json['refresh_token']
        tokens['refresh_token'] = new_refresh_token
    
    return tokens