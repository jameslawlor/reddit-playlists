from functions.spotipy import get_subreddit_from_playlist_name


def test_get_subreddit_from_playlist_name():

    test_playlists = [
        "/r/Techno top weekly tracks",
        "/r/Outrun top weekly tracks",
        "/r/house top weekly tracks",
        "/r/hardstyle top weekly tracks",
    ]
    expected_output = ["Techno", "Outrun", "house", "hardstyle"]

    for (playlist, expected_subreddit_name) in zip(test_playlists, expected_output):
        assert expected_subreddit_name == get_subreddit_from_playlist_name(
            playlist, "/r/{} top weekly tracks"
        )
