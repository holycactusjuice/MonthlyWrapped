import pymongo
from pymongo import MongoClient

password = '4qlOBbwf5PvVRr80'

cluster = MongoClient(
    f'mongodb+srv://cactus:{password}@cluster0.t4brvzm.mongodb.net/test?retryWrites=true&w=majority')

db = cluster['test']
collection = db['test']

post = {'name': 'cactus', 'age': 17}

collection.insert_many(post)
