from models import User
from . import users

def update_db():
    users = users.find()
    for user_document in users:
        user = User.from_document(user_document)
        user.update_listen_data()
