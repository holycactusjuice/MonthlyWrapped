from . import db
from mongoengine import Document, StringField, BooleanField, DateTimeField, IntField, ListField, EmbeddedDocument, DictField
from flask_login import UserMixin


class User(UserMixin, Document):
    # spotify_username = StringField(required=True, unique=True)
    spotify_email = StringField(required=True, unique=True)
    # password = StringField(required=True)
    listen_data = DictField(default={})
    id = IntField(primary_key=True, unique=True, required=True)

    def __init__(self):
        pass

    @staticmethod
    def is_authenticated():
        return True


class Track(EmbeddedDocument):
    title = StringField(required=True)
    artists = ListField(required=True)
    album = StringField(required=True)
    art = StringField(required=True)  # url for album art
    length = IntField(required=True)  # in seconds
    id = StringField(primary_key=True, unique=True,
                     required=True)  # same as Spotify ID
