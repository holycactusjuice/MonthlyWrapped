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

    def update_listen_data(self, track):
        """
        Updates the user's listen data given a track object

        Args:
            self (user)
            track (Track): track object to be added to user's listen data
        Returns:
            None (updates user listen data in place)
        """
        track_info = track
        # if the track isn't already in the user's listen data, add it
        if track.track_id not in [track['track_id'] for track in self.listen_data]:
            self.listen_data.append(track.__dict__)

        track_id = track.track_id
        last_listen = track.last_listen

        # if track.last_listen is greater than the last_listen stored in the user's data
        # then this listen has not yet been recorded
        query = {'listen_data.track_id': track_id}
        user_track_data = users.find_one
        if last_listen > self.listen_data[track_id]['last_listen']:
            # update the following fields:
            #   - last listen
            #   - listen count
            #   - total listen time
            self.listen_data[track_id]['last_listen'] = last_listen
            time_listened = track.time_listened
            self.listen_data[track_id]['time_listened'] += time_listened
            self.listen_data[track_id]['listen_count'] += 1

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
