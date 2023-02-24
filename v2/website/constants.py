import os
import base64
import time
from dotenv import load_dotenv

load_dotenv()

CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_KEY = os.getenv("MONGODB_KEY")
DB_NAME = "monthlyWrappedDB"

CLIENT_CREDS = f"{CLIENT_ID}:{CLIENT_SECRET}"
CLIENT_CREDS_B64 = base64.b64encode(CLIENT_CREDS.encode()).decode()

TOKEN_URL = "https://accounts.spotify.com/api/token"

RESPONSE_TYPE = "code"
SCOPES = ["playlist-modify-public", "playlist-modify-private",
          "ugc-image-upload", "user-read-recently-played", "user-read-private", "user-read-email",]
AUTH_URL = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type={RESPONSE_TYPE}&redirect_uri={REDIRECT_URI}&scope={'%20'.join(SCOPES)}"

endpoints = {
    "create_playlist": "https://api.spotify.com/v1/me/playlists",
    "get_recently_played": "https://api.spotify.com/v1/me/player/recently-played",
    "get_user": "https://api.spotify.com/v1/me",
}

# add 5 hours to convert to GMT, multiply by 1000 to get milliseconds
TIME = (time.time() + 5 * 60 * 60) * 1000
