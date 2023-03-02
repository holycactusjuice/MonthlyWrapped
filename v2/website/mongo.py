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


def insert():
    document = {
        'name': 'Mr. Gibson',
        'students': [
            {
                'name': 'Yiyan',
                'age': '17'
            },
            {
                'name': 'Annika',
                'age': 18
            }
        ]
    }
    users.insert_one(document)


def update():
    student = {
        'name': 'Patrick',
        'age': 17
    }
    users.update_one({'name': 'Mr. Gibson'}, {
                     "$addToSet": {'students': student}})


def find():
    l = users.find({'students': {'name': 'Patrick'}})
    return l


people = find()
print(list(people))
