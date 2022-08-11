from functions.reddit import get_reddit_client
from functions.spotipy import get_spotipy_client


def test_get_reddit_client():
    get_reddit_client()


def test_get_spotipy_client():
    get_spotipy_client("client_authorization_code_flow")
