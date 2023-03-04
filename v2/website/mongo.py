from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_KEY = os.getenv("MONGODB_KEY")
DB_NAME = "monthlyWrappedDB"

client = MongoClient(
    f'mongodb+srv://cactus:{MONGODB_PASSWORD}@cluster0.t4brvzm.mongodb.net/test?retryWrites=true&w=majority')
db = client[DB_NAME]
users = db['users']
tracks = db['tracks']


def get_user_document(user_id):
    return users.find_one({'_id': user_id})
