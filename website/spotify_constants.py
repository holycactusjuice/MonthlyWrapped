import os
import base64
import time
from dotenv import load_dotenv

load_dotenv()

CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")

RESPONSE_TYPE = "code"
REQUIRED_SCOPES = ["playlist-modify-public", "playlist-modify-private",
                   "ugc-image-upload", "user-read-recently-played", "user-read-private", "user-read-email",]
SCOPE = "%20".join(REQUIRED_SCOPES)

CLIENT_CREDS = f"{CLIENT_ID}:{CLIENT_SECRET}"
CLIENT_CREDS_B64 = base64.b64encode(CLIENT_CREDS.encode()).decode()

TOKEN_URL = "https://accounts.spotify.com/api/token"

AUTH_URL = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type={RESPONSE_TYPE}&redirect_uri={REDIRECT_URI}&scope={SCOPE}"

ACCESS_TOKEN = "BQBQURNyRIxt9V_xaQngPy865mCnzDiRDGW8VMZbUsfcsm-m8ESI7zdQsmEDzKtNPo8a9yo8VrWwDxacnLsOnFMh9jKVb-28JLaWtPeJZsDBULdjoRCIWjJxyTLgI2pf5vJ8R6svMKkz5792X8V2JceYVl3LbCc_DxLN0iI96wKinx4uSMIQPaAn7A"

CREATE_PLAYLIST_ENDPOINT = "https://api.spotify.com/v1/users/arashinsavage/playlists"
GET_CURRENT_TRACK_ENDPOINT = "https://api.spotify.com/v1/me/player/currently-playing"
GET_RECENT_TRACKS_ENDPOINT = "https://api.spotify.com/v1/me/player/recently-played"
GET_USER_ENDPOINT = "https://api.spotify.com/v1/me"


# current time since epoch in milliseconds
MS_SINCE_EPOCH = time.time() * 1000 + 5 * 60 * 60 * 1000
