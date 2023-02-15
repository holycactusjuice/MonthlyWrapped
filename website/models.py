from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(20))
    # listen_data = db.Column(JSONB)
