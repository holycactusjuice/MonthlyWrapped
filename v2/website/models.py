from . import db
from mongoengine import Document, StringField, IntField, ListField, DictField, EmbeddedDocumentField


class User(Document):
    spotify_username = StringField(required=True, unique=True)
    spotify_email = StringField(required=True, unique=True)
    listen_data = DictField(required=True, default={})
    id = IntField(primary_key=True, required=True, unique=True)


class Track(Document):
    title = StringField(required=True)
    artists = ListField(StringField(), required=True)
    album = StringField(required=True)
    art = StringField(required=True)  # url for album art
    length = IntField(required=True)  # in seconds
    id = StringField(primary_key=True, required=True,
                     unique=True)  # same as spotify_id
