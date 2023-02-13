import requests
import json
import time

# Replace <client_id> and <client_secret> with your own Spotify API credentials
client_id = "4a8a27479cb048bdb4a0b5aa0672ae8b"
client_secret = "d5513e7039ae4454be2355e7b885d350"

# Get an access token
auth_response = requests.post("https://accounts.spotify.com/api/token",
                              data={"grant_type": "client_credentials"},
                              auth=(client_id, client_secret))

access_token = auth_response.json()["access_token"]

# Get the user's recent tracks
headers = {
    "Authorization": f"Bearer {access_token}"
}

recent_tracks_response = requests.get(
    "https://api.spotify.com/v1/me/player/recently-played", headers=headers)

recent_tracks = recent_tracks_response.json()["items"]

# Print the name of each track and the duration it was played for
for i, track in enumerate(recent_tracks):
    print(f"Track: {track['track']['name']}")
    played_at = int(time.mktime(time.strptime(
        track["played_at"], '%Y-%m-%dT%H:%M:%S.%fZ')))
    if i + 1 < len(recent_tracks):
        next_played_at = int(time.mktime(time.strptime(
            recent_tracks[i + 1]["played_at"], '%Y-%m-%dT%H:%M:%S.%fZ')))
        duration = next_played_at - played_at
        print(f"Duration played: {duration} seconds\n")
    else:
        print("Duration played: Unknown (this was the last played track)\n")
