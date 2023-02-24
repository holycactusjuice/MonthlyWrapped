from flask import Flask
from flask_login import LoginManager
from pymongo import MongoClient
from flask_pymongo import PyMongo

PASSWORD = '4qlOBbwf5PvVRr80'
SECRET_KEY = 'key'

client = MongoClient(
    f'mongodb+srv://cactus:{PASSWORD}@cluster0.t4brvzm.mongodb.net/test?retryWrites=true&w=majority')
db = client['spotify-app']
users = db['users']


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/test'
    mongo = PyMongo(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = ('auth.login')
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
