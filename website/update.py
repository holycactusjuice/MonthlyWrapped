from .models import User
from . import users

users = users.find()
print(users)