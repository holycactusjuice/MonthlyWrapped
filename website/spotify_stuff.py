import requests
import time
import json
import datetime

ACCESS_TOKEN = "BQCQYtmYqSZgXo82gO7m9AvaPKshMDpCeF5bO1tt3iYk9oVzMvqNBmIQ7KAfoSqH5xYuKcDISb6WcARI9d62xyh0aGFd8USRGsXyzXaXWQhPP0lt2kmEYOvJNMB_3hghU54eBKO30WmaHXEQO3SAxujPyAToC0hN1M7No9Sfs2hAptTANdPFVJJUVg"

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
        tracks (dict): dictionary of track_id : track info
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

    tracks = {}

    recent_tracks = resp_json["items"]
    # reverse list since the last played track is given first
    recent_tracks.reverse()

    track_names = [item["track"]["name"] for item in resp_json["items"]]

    for i, track in enumerate(recent_tracks):
        # print(track)

        track_id = track['track']['id']

        if track_id not in tracks:

            track_data = get_track_data(track)
            tracks[track_id] = track_data

        # get the time this track ended in unix timestamp
        # time_string is the format: 2023-02-12T17:18:28.679Z
        played_at = played_at_unix(track['played_at'])

        # if not first track in list and this listen has not been recorded
        if i != 0 and played_at not in tracks[track_id]["listen_data"]:

            track_length = int(tracks[track_id]['track_length'] / 1000)

            # get the time the last track ended in unix timestamp
            last_track = recent_tracks[i - 1]
            last_played_at = played_at_unix(last_track['played_at'])

            # duration is the difference between when the last track ended (when this track started) and when this track ended
            duration = played_at - last_played_at

            # duration may be greater than track length if:
            #   - the user took a break before playing the track
            #   - the user paused the track
            #   - this is the first song in the session
            # so if duration > track_length, make duration = track_length
            duration = min(duration, track_length)

            # add this listen to the user's data
            tracks[track_id]["listen_data"][played_at] = duration

    return tracks


def played_at_unix(played_at):
    return int(datetime.datetime.strptime(
        played_at, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())


def get_track_data(track):
    """
    Gets the track data given a track json
    """
    # track_id = track['track']['id']
    track_name = track['track']['name']
    track_length = int(track['track']['duration_ms'] / 1000)
    track_artists = [artist["name"]
                     for artist in track["track"]["artists"]]
    track_album = track["track"]["album"]

    album_name = track_album["name"]
    album_artist = track_album["artists"][0]["name"]
    album_art_url = track_album["images"][0]["url"]

    track_data = {
        # "track_id": track_id,
        "track_name": track_name,
        "track_length": track_length,
        "track_artists": track_artists,
        "album": {
            "album_name": album_name,
            "album_artist": album_artist,
            "album_art_url": album_art_url,
        },
        "listen_data": {
        },
    }

    return track_data


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


if __name__ == '__main__':
    main()
