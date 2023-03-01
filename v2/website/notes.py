"""
format for user.listen_data

[
    {
        track1_id (str): 'track1_id',
        title (str): 'title',
        artists (list): ['artist1', 'artist2'],
        album (str): 'album',
        album_art_url (str): 'album_art_url',
        listen_data (dict): {
            last_listen_time (int): 1234567890,
            listen_count (int): 123,
            total_listen_time (int): 123456
    },
    {
        track2_id (str): 'track2_id',
        title (str): 'title',
        artists (list): ['artist1', 'artist2'],
        album (str): 'album',
        album_art_url (str): 'album_art_url',
        listen_data (dict): {
            last_listen_time (int): 1234567890,
            listen_count (int): 123,
            total_listen_time (int): 123456
    },
]
"""
