import pymongo
from pymongo import MongoClient
from spotify_stuff import get_recent_tracks, GET_RECENT_TRACKS_ENDPOINT, ACCESS_TOKEN

password = '4qlOBbwf5PvVRr80'

cluster = MongoClient(
    f'mongodb+srv://cactus:{password}@cluster0.t4brvzm.mongodb.net/test?retryWrites=true&w=majority')

db = cluster['test']
collection = db['test']

# recent_tracks = get_recent_tracks(ACCESS_TOKEN, 3)

post = {'name': 'cactus', 'age': 17}
collection.insert_one(post)
# x = collection.insert_one(recent_tracks)
# print(x)
