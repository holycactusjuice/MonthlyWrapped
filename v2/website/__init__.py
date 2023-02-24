from flask import Flask
from flask_login import LoginManager
from pymongo import MongoClient
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_KEY = os.getenv("MONGODB_KEY")
DB_NAME = "monthlyWrappedDB"


client = MongoClient(
    f'mongodb+srv://cactus:{MONGODB_PASSWORD}@cluster0.t4brvzm.mongodb.net/test?retryWrites=true&w=majority')
db = client[DB_NAME]
users = db['users']
tracks = db['tracks']


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = MONGODB_KEY
    app.config['MONGO_URI'] = f'mongodb://localhost:27017/{DB_NAME}'

    mongo = PyMongo()
    mongo.init_app(app)

    # from .views import views
    from .auth import auth

    # app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Track

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return  # get user from db

    return app
