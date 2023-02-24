import requests
import json
import datetime
import base64
from .constants import *
import string
import secrets
from urllib.parse import urlencode
from flask import redirect


def get_access_token(client_id, client_secret, redirect_uri):
    """
    Get access token for the given client_id and client_secret
    """

    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = TOKEN_URL
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic' + auth_base64
    }


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