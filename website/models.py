from . import users
from mongoengine import Document, EmbeddedDocument, StringField, IntField, ListField, EmailField, ObjectIdField, EmbeddedDocumentField
from flask_login import UserMixin
from bson import ObjectId
from email.message import EmailMessage
import requests
import json
import ssl
import smtplib
import math

from .constants import endpoints, CLIENT_CREDS_B64, TIME, EMAIL_PASSWORD
from .misc import played_at_unix


class Track(EmbeddedDocument):
    """
    Class to represent a Spotify track

    Attributes:
        title (str): title of track
        artist (str): artist of track
        album_art_url (str): album to which track belongs
        art (str): album art url
        length (int): length of track in seconds
        id (str): Spotify id of track
    """
    title = StringField(required=True)
    artists = ListField(StringField(), required=True)
    album = StringField(required=True)
    album_art_url = StringField(required=True)  # url for album art
    length = IntField(required=True)  # in seconds
    id = StringField(primary_key=True, required=True,
                     unique=True)  # same as spotify_id

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

    @classmethod
    def from_json(cls, track_json):
        """
        Creates a Track object from a track JSON

        Args:
            track_json (dict): track json received from Spotify API
        Returns:
            track (Track): Track object with track data
        """

        # retrieve track data from track JSON returned by Spotify API

        track_id = track_json['track']['id']
        title = track_json['track']['name']
        artists = [artist["name"]
                   for artist in track_json["track"]["artists"]]
        album = track_json["track"]["album"]["name"]
        album_art_url = track_json["track"]["album"]["images"][0]["url"]
        length = int(track_json['track']['duration_ms'] / 1000)

        # instantiate Track object from these dat
        track = Track(track_id, title, artists, album, album_art_url, length)

        return track


class User(UserMixin, Document):
    """
    Class to represent a user

    Attributes:
        username (str): user's spotify username
        email (str): user's spotify email address
        display_name (str): user's spotify display name
        pfp (str): user's spotify profile picture image url
        listen_data (dict): user's spotify listen data
        time_last_updated ()
        _id (ObjectId): user's id in the database
    """
    _id = ObjectIdField(primary_key=True, required=True, unique=True)
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    display_name = StringField(required=True)
    pfp = StringField()
    access_token = StringField()
    refresh_token = StringField()
    listen_data = ListField(EmbeddedDocumentField(
        Track), required=True, default=[])

    def __init__(self, _id, username, email, display_name, pfp, access_token, refresh_token, listen_data=[], *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        self._id = _id
        self.username = username
        self.email = email
        self.display_name = display_name
        self.pfp = pfp
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.listen_data = listen_data

    def dict(self):
        """
        Returns a dictionary representation of the User object
        - useful for initial insert into MongoDB

        Args:
            self (User)
        Returns:
            info (dict): dictionary representation of the user's information
        """
        info = {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'pfp': self.pfp,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'listen_data': self.listen_data
        }
        return info

    def get_id(self):
        """
        Returns the user's id from MongoDB
        - required for Flask's login manager

        Args:
            self (User)
        Returns:
            self._id (str)
        """
        return str(self._id)

    def get_access_token(self):
        """
        Gets the user's access token from MongoDB

        Args:
            self (User)
        Returns:
            access_token (str): the user's current access token
        """
        user_document = users.find_one({'_id': ObjectId(self._id)})
        access_token = user_document['access_token']
        return access_token

    def get_refresh_token(self):
        """
        Gets the user's refresh token from MongoDB

        Args:
            self (User)
        Returns:
            refresh_token (str): the user's current refresh token
        """
        user_document = users.find_one({'_id': ObjectId(self._id)})
        refresh_token = user_document['refresh_token']
        return refresh_token

    def get_listen_data(self):
        """
        Gets the user's listen data from MongoDB

        Args:
            self (User)
        Returns:
            listen_data (list)
        """
        user_document = users.find_one({'_id': ObjectId(self._id)})
        listen_data = user_document['listen_data']
        return listen_data

    def get_recent_tracks(self, limit=50):
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
            limit (int): number of tracks to return

        Returns:
            tracks (list): list of Track objects
        """

        # kwargs for GET request
        url = endpoints['get_recently_played']
        headers = {
            "Authorization": f"Bearer {self.access_token}"
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

        # if the response gives a 401 or 403 error, the access token has expired
        # return -1 to indicate this
        if response.status_code in (401, 403):
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

            track = Track.from_json(track_json)

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


    def swap_tokens(self):
        """
        Swaps the current refresh token for a new access token (and refresh token if the last one has expired)

        Args:
            self (User)
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
            'refresh_token': self.refresh_token
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

    def update_tokens(self):
        """
        Updates the current tokens by sending a request to the Spotify API with the user's current refresh token

        Args:
            self (User)
        Returns:
            None (updates tokens in MongoDB)
        """
        tokens = self.swap_tokens()

        new_access_token = tokens['access_token']

        # update refresh token only if a new one has been issued
        if 'refresh_token' in tokens:
            new_refresh_token = tokens['refresh_token']
            users.update_one({'username': self.username}, {'$set': {
                             'access_token': new_access_token, 'refresh_token': new_refresh_token}})
        else:
            users.update_one({'username': self.username}, {
                             '$set': {'access_token': new_access_token}})

    def get_top_tracks_by_listen_count(self, n):
        """
        Returns a list of the user's top n tracks based on listen count

        Args:
            self (User)
            n (int): number of top tracks to return
        Returns:
            top_tracks (list): list of user's top n tracks based on listen count
        """
        listen_data = self.get_listen_data()
        listen_data.sort(key=lambda x: x['listen_count'], reverse=True)

        top_tracks = listen_data[:n]

        return top_tracks

    def get_top_tracks_by_time_listened(self, n):
        """
        Returns a list of the user's top n tracks based on time listened

        Args:
            self (User)
            n (int): number of top tracks to return
        Returns:
            top_tracks (list): list of user's top n tracks based on time listened
        """
        listen_data = self.get_listen_data()
        listen_data.sort(key=lambda x: x['time_listened'], reverse=True)

        top_tracks = listen_data[:n]

        return top_tracks

    def update_listen_data(self):
        """
        Updates the user's listen data in MongoDB

        Args:
            self (User)
        Returns:
            None (only updates database)
        """
        recent_tracks = self.get_recent_tracks()

        if recent_tracks == -1:
            self.update_tokens()
            recent_tracks = self.get_recent_tracks()

        for track in recent_tracks:
            # update the following fields:
            #   - last_listen
            #   - listen_count
            #   - time_listened
            result = users.find_one(
                {
                    'username': self.username,
                    'listen_data': {'$elemMatch': {'track_id': track.track_id}}
                },
                {'listen_data.$': 1}
            )
            if result:
                # check if this listen has already been recorded
                # if last_listen > the track to be added's last_listen, then add it
                if track.last_listen > result['listen_data'][0]['last_listen']:
                    query = {'username': self.username,
                             'listen_data.track_id': track.track_id}
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
                query = {'username': self.username}
                update = {'$push': {'listen_data': track.__dict__}}
                users.update_one(query, update)

    def create_playlist(self, name, description, public=False):
        """
        Creates a new playlist in the user's account

        Args:
            name (str): name of playlist
            description (str): description of playlist
            public (bool): playlist will be public if true, else false. defaults to false

        Returns:
            playlist_id (str): ID of playlist
        """
        username = self.username
        access_token = self.access_token
        url = f"https://api.spotify.com/v1/users/{username}/playlists"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = json.dumps({
            'name': name,
            'description': description,
            'public': public
        })
        response = requests.post(url, headers=headers, data=data)
        response_data = response.json()

        playlist_id = response_data['id']
        print(f'PLAYLIST ID: {playlist_id}')

        return playlist_id

    def append_tracks_to_playlist(self, playlist_id, track_ids):
        """
        Appends a track to a user's playlist

        Args:
            playlist_id (str): Spotify playlist ID
            track_id (list): Spotify track IDs
        """

        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = {
            'Authorization': f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        data = {
            'uris': track_ids
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))

    def create_new_monthly_wrapped(self, name, description, public=False):
        """
        Creates a new monthly wrapped playlist in the user's account

        Args:
            self (User)
            name (str): name of playlist
            description (str): description of playlist
            public (bool, optional): playlist is public if true. Defaults to False.
        """
        self.update_tokens()

        playlist_id = self.create_playlist(name, description, public)
        top_tracks = self.get_top_tracks_by_listen_count(100)

        track_ids = []

        for track in top_tracks:
            track_id = track['track_id']
            track_ids.append(f'spotify:track:{track_id}')

        self.append_tracks_to_playlist(playlist_id, track_ids)

    def email_listen_data(self, formatted=False):
        """
        Sends an email to the user's Spotify email address containing their listening data

        Args
            self (User)
            formatted (bool): if false, raw data will be sent; if true, formatted data will be sent

        Returns
            None
        """
        email_sender = 'monthlyWrapped@gmail.com'
        email_password = EMAIL_PASSWORD
        email_receiver = self.email

        subject = 'Test Email'

        if not formatted:
            body = str(self.get_listen_data())
        else:
            pass

        email = EmailMessage()
        email['From'] = email_sender
        email['To'] = email_receiver
        email['Subject'] = subject
        email.set_content(body)

        print(email)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, email.as_string())

        return

    def clear_listen_data(self):
        """
        Clears the user's listen data in MongoDB
        """
        result = users.find_one({'username': self.username})

        if result:
            query = {'username': self.username}
            update = {'$set': {'listen_data': []}}
            users.update_one(query, update)

    def get_total_time_listened(self):
        """
        Returns the user's total listen time in seconds

        Returns:
            total_time_listened (int): the user's total listen time in seconds
        """
        listen_data = self.get_listen_data()
        total_seconds_listened = 0
        for track in listen_data:
            seconds_listened = track['time_listened']
            total_seconds_listened += seconds_listened
            
        seconds = total_seconds_listened % 60
        minutes = math.floor((total_seconds_listened % 3600) / 60)
        hours = math.floor(total_seconds_listened / 3600)
        
        total_time = {}
        total_time['seconds'] = seconds
        total_time['minutes'] = minutes
        total_time['hours'] = hours
        
        return total_time
    
    def get_total_listen_count(self):
        """
        Returns the user's total listen count

        Returns:
            total_listen_count (int): the user's total listen count
        """
        listen_data = self.get_listen_data()
        total_listen_count = 0
        for track in listen_data:
            listen_count = track['listen_count']
            total_listen_count += listen_count
        return total_listen_count
    
    def get_total_track_count(self):
        """
        Returns the number of tracks that the user has listened to

        Returns:
            total_track_count (int): number of tracks that the user has listened to
        """
        listen_data = self.get_listen_data()
        total_track_count = len(listen_data)
        return total_track_count
    
    @classmethod
    def get_account_info(cls, access_token):
        """
        Gets a user's account information from Spotify API

        Args:
            access_token (str): user access token

        Returns:
            dict: user's account information in json format
        """
        url = endpoints['get_user']
        headers = {
            "Authorization": "Bearer " + access_token,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.get(
            url=url, headers=headers
        )
        return response.json()

    @classmethod
    def from_email(cls, email):
        """
        Gets a User object by email address from the database
        """
        user_doc = users.find_one({"email": email})

        return User.from_document(user_doc)

    @classmethod
    def from_username(cls, username):
        """
        Gets a User object by username from the database
        """
        user_doc = users.find_one({"username": username})

        return User.from_document(user_doc)

    @classmethod
    def from_document(cls, user_doc):
        """
        Creates a User object from a dictionary retrieved from MongoDB
        """
        _id = str(user_doc['_id'])
        username = user_doc['username']
        email = user_doc['email']
        display_name = user_doc['display_name']
        pfp = user_doc['pfp']
        access_token = user_doc['access_token']
        refresh_token = user_doc['refresh_token']

        return User(_id, username, email, display_name, pfp, access_token, refresh_token)