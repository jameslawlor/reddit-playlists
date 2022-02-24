from functions.spotipy import (
    get_subreddit_from_playlist_name,
    unify_data,
    get_subreddits_with_existing_playlists,
    get_subreddits_without_existing_playlists,
)


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


def test_unify_data():
    cleaned_subreddit_dic = {
        "EDM": {"genre": "Electronic music", "subscribers": 1569659},
        "ElectronicMusic": {"genre": "Electronic music", "subscribers": 2234687},
        "metal": {"genre": "Rock/Metal", "subscribers": 1434536},
        "hiphopheads": {"genre": "Hip-hop", "subscribers": 2029284},
        "kpop": {"genre": "By country/region/culture", "subscribers": 1232967},
    }

    existing_playlists = [
        {
            "playlist_name": "/r/kpop top weekly tracks",
            "id": "6BWdRZ254hVUI0wDxjXpvb",
            "subreddit": "kpop",
        },
        {
            "playlist_name": "/r/hiphopheads top weekly tracks",
            "id": "7erepqmQxL7HhZPn48YjTt",
            "subreddit": "hiphopheads",
        },
    ]

    expected_output = {
        "EDM": {"genre": "Electronic music", "subscribers": 1569659},
        "ElectronicMusic": {"genre": "Electronic music", "subscribers": 2234687},
        "metal": {"genre": "Rock/Metal", "subscribers": 1434536},
        "hiphopheads": {
            "genre": "Hip-hop",
            "subscribers": 2029284,
            "playlist_name": "/r/hiphopheads top weekly tracks",
            "id": "7erepqmQxL7HhZPn48YjTt",
            "subreddit": "hiphopheads",
        },
        "kpop": {
            "genre": "By country/region/culture",
            "subscribers": 1232967,
            "playlist_name": "/r/kpop top weekly tracks",
            "id": "6BWdRZ254hVUI0wDxjXpvb",
            "subreddit": "kpop",
        },
    }

    output = unify_data(cleaned_subreddit_dic, existing_playlists)
    assert output == expected_output


def test_get_subreddits_with_existing_playlists():

    input = {"A": {"id": "blah"}, "B": {"id": "blah"}, "C": {}}
    expected_output = ["A", "B"]

    assert expected_output == get_subreddits_with_existing_playlists(input)


def test_get_subreddits_without_existing_playlists():

    input = {"A": {"id": "blah"}, "B": {"id": "blah"}, "C": {}}
    expected_output = ["C"]

    assert expected_output == get_subreddits_without_existing_playlists(input)
