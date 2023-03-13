from . import users
from mongoengine import Document, EmbeddedDocument, StringField, IntField, ListField, DictField, EmailField, ObjectIdField, EmbeddedDocumentField
from flask_login import UserMixin
from bson import ObjectId

from .spotify import swap_tokens, get_recent_tracks


class Track(EmbeddedDocument):
    title = StringField(required=True)
    artists = ListField(StringField(), required=True)
    album = StringField(required=True)
    art = StringField(required=True)  # url for album art
    length = IntField(required=True)  # in seconds
    id = StringField(primary_key=True, required=True,
                     unique=True)  # same as spotify_id


class User(UserMixin, Document):
    """
    Class to represent a user

    Attributes:
        username (str): user's spotify username
        email (str): user's spotify email address
        display_name (str): user's spotify display name
        pfp (str): user's spotify profile picture image url
        listen_data (dict): user's spotify listen data
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
            listen_data (dict)
        """
        user_document = users.find_one({'_id': ObjectId(self._id)})
        listen_data = user_document['listen_data']
        return listen_data
    
    # def update_user(self):
    #     """
    #     Updates the user's listen data by retrieving info from the database

    #     Args:
    #         self (user)
    #     Returns:
    #         None (updates user listen data in place)
    #     """
    #     username = self.username
    #     user_doc = users.find_one({'username': username})
    #     self.email = user_doc['email']
    #     self.display_name = user_doc['display_name']
    #     self.pfp = user_doc['pfp']
    #     self.listen_data = user_doc['listen_data']

    def update_tokens(self):
        """
        Updates the current tokens by sending a request to the Spotify API with the user's current refresh token

        Args:
            self (User)
        Returns:
            None (updates tokens in MongoDB)
        """
        refresh_token = self.get_refresh_token()
        tokens = swap_tokens(refresh_token)
        
        new_access_token = tokens['access_token']
        
        # update refresh token only if a new one has been issued
        if 'refresh_token' in tokens:
            new_refresh_token = tokens['refresh_token']
            users.update_one({'username': self.username}, {'$set': {'access_token': new_access_token, 'refresh_token': new_refresh_token}})
        else:
            users.update_one({'username': self.username}, {'$set': {'access_token': new_access_token}})

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
        access_token = self.get_access_token()
        recent_tracks = get_recent_tracks(access_token)
        
        if recent_tracks == -1:
            self.update_tokens()
            access_token = self.get_access_token()
            recent_tracks = get_recent_tracks(access_token)
        
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
                    query = {'username': self.username, 'listen_data.track_id': track.track_id}
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
                    {'username': self.username},
                    {'$push': {'listen_data': track.__dict__}}
                )
        

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
