import requests
import time
import json
import datetime

ACCESS_TOKEN = "BQAOFZ6PYRgQgy5fXvtqpuN5tNNQOz1SLz5oKDnGzfdF5Wk9f2NAUsU37nCijS968iF0S5G-WA4-gluAqR3yvyLz7y0_fjJ_zh_w5K_n5QDbfyWq1vc6G26Zva0oRGDm0FfAk1S9H9K-j2y4NtJSQzJnSnsXnqtjLtnP2HYp5hn0FrmA9ITs8kjEeQ"

CREATE_PLAYLIST_ENDPOINT = "https://api.spotify.com/v1/users/arashinsavage/playlists"
GET_CURRENT_TRACK_ENDPOINT = "https://api.spotify.com/v1/me/player/currently-playing"
GET_RECENT_TRACKS_ENDPOINT = "https://api.spotify.com/v1/me/player/recently-played"
GET_TOP_ITEMS_ENDPOINT = "https://api.spotify.com/v1/me/top/tracks"

# current time since epoch in milliseconds
MS_SINCE_EPOCH = time.time() * 1000 + 5 * 60 * 60 * 1000


def create_playlist(access_token, name, description, public):
    """
    Creates a playlist

    Args:
        access_token (str): access token from Spotify API to grant persmissions
        name (str): name of playlist
        description (str): description of playlist
        public (bool): True if playlist should be public, False if private

    Returns:
        json_resp (dict): dictionary representation of the json from the request response
    """

    # post request
    response = requests.post(
        CREATE_PLAYLIST_ENDPOINT,
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "name": name,
            "description": description,
            "public": public
        }
    )
    json_resp = response.json()
    return json_resp


def get_current_track(access_token):

    response = requests.get(
        GET_CURRENT_TRACK_ENDPOINT,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    resp_json = response.json()

    track_id = resp_json["item"]["id"]
    track_name = resp_json["item"]["name"]
    artists_names = ", ".join(
        [artist["name"] for artist in resp_json["item"]["artists"]]
    )
    link = resp_json["item"]["external_urls"]["spotify"]

    current_track_info = {
        "id": track_id,
        "name": track_name,
        "artists": artists_names,
        "link": 'link'
    }

    return current_track_info


def get_recent_tracks(access_token, limit):
    """
    Gets user's recent tracks with the following information:
        - track name
        - artist name(s)
        - album
        - time played at
        - duration played for

    Args:
        access_token (str): access token from Spotify API to grant persmissions
        limit (int): number of recent tracks to get (bewteen 1 and 50)

    Returns:

    """
    response = requests.get(
        GET_RECENT_TRACKS_ENDPOINT,
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        params={
            # IMPORTANT: before is in ms, must be int
            "before": int(MS_SINCE_EPOCH),
            # limit must be bewteen 1 and 50 inclusive
            "limit": limit
        }
    )
    print(response)
    resp_json = response.json()
    # print(resp_json)
    recent_tracks = resp_json["items"]
    # reverse list since the last played track is given first
    recent_tracks.reverse()

    track_names = [item["track"]["name"] for item in resp_json["items"]]

    for i, track in enumerate(recent_tracks):
        print(f"Track: {track['track']['name']}")

        track_title = track['track']['name']
        track_length = int(track['track']['duration_ms'] / 1000)
        track_id = track['track']['id']
        artists = [artist["name"] for artist in track["track"]["artists"]]
        album = track["track"]["album"]["name"]

        # played_at is in seconds since epoch
        # time_string is the format: 2023-02-12T17:18:28.679Z
        time_string = track['played_at']
        played_at = int(datetime.datetime.strptime(
            time_string, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
        print(played_at)

        # if not first track in list
        if i != 0:
            last_track = recent_tracks[i - 1]
            last_time_string = last_track['played_at']

            last_played_at = int(datetime.datetime.strptime(
                last_time_string, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())

            duration = played_at - last_played_at
            print(duration, track_length)
            if duration >= track_length:
                print(f"Duration played: {track_length} seconds\n")
            else:
                print("idk\n")
        # if first track in list
        else:
            print("Duration played: Unknown (this was the first played track)\n")

    # print("current time:", int(MS_SINCE_EPOCH / 1000))

    # with open('test.txt', 'w') as f:
    #     f.write(json.dumps(resp_json))

    return track_names


def get_top_items(access_token):
    response = requests.get(
        GET_TOP_ITEMS_ENDPOINT,
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        params={
            "limit": 50,
            "time_range": "long_term",
        }
    )
    print(response)
    resp_json = response.json()

    top_artists = [item['name'] for item in resp_json['items']]

    return top_artists


def main():

    # playlist = create_playlist(
    #     name="My Playlist",
    #     description="test",
    #     public=False
    # )

    # print("Playlist:", playlist)

    # current_track = get_current_track(ACCESS_TOKEN)
    # print(current_track)

    recent_tracks = get_recent_tracks(ACCESS_TOKEN, 10)
    for track in recent_tracks:
        print(track)
    get_recent_tracks(ACCESS_TOKEN, 50)

    # top = get_top_items(ACCESS_TOKEN)
    # print(top)


if __name__ == '__main__':
    main()
