from . import users
from mongoengine import Document, EmbeddedDocument, StringField, IntField, ListField, DictField, EmailField, ObjectIdField, EmbeddedDocumentField
from flask_login import UserMixin


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
        listen_data (dict): user's spotify listen data
        pfp (str): user's spotify profile picture image url
        _id (ObjectId): user's id in the database
    """
    _id = ObjectIdField(primary_key=True, required=True, unique=True)
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    display_name = StringField(required=True)
    listen_data = ListField(EmbeddedDocumentField(
        Track), required=True, default=[])
    pfp = StringField()

    def __init__(self, _id, username, email, display_name, pfp, listen_data=[], *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        self._id = _id
        self.username = username
        self.email = email

        self.display_name = display_name
        self.pfp = pfp
        self.listen_data = listen_data

    def dict(self):
        """
        Returns a dictionary representation of the User object
            * useful for inserting into MongoDB
        """
        info = {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'listen_data': self.listen_data,
            'pfp': self.pfp,
        }
        return info

    def get_id(self):
        return str(self._id)

    def update_user(self):
        """
        Updates the user's listen data by retrieving info from the database

        Args:
            self (user)
        Returns:
            None (updates user listen data in place)
        """
        username = self.username
        user_doc = users.find_one({'username': username})
        self.email = user_doc['email']
        self.display_name = user_doc['display_name']
        self.pfp = user_doc['pfp']
        self.listen_data = user_doc['listen_data']

    def get_top_tracks_by_listen_count(self, n):
        """
        Returns a list of the user's top n tracks based on listen count

        Args:
            self (User)
            n (int): number of top tracks to return
        Returns:
            top_tracks (list): list of user's top n tracks based on listen count
        """
        self.update_user()

        listen_data = self.listen_data
        listen_data.sort(key=lambda x: x['listen_count'], reverse=True)

        top_tracks = listen_data[:n]

        return top_tracks

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
        listen_data = user_doc['listen_data']
        pfp = user_doc['pfp']

        return User(_id, username, email, display_name, pfp, listen_data)
