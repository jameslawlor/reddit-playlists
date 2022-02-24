import configparser
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from functions.base_logger import logger
import re


def get_spotipy_client():

    config = configparser.ConfigParser()
    config.read("spotipy.cfg")
    client_id = config.get("SPOTIFY", "CLIENT_ID")
    client_secret = config.get("SPOTIFY", "CLIENT_SECRET")
    username = config.get("SPOTIFY", "USERNAME")

    scope = ("playlist-modify-public",)
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret,
    )
    auth_manager = SpotifyOAuth(
        scope=scope,
        username=username,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:8888/callback/",
    )

    sp = spotipy.Spotify(
        client_credentials_manager=client_credentials_manager, auth_manager=auth_manager
    )

    return sp, username


def clean_subreddits(
    subreddit_genre_sub_counts,
    genres_whitelist,
    subreddit_blacklist,
    subscriber_min_count: int,
):

    logger.info("Cleaning list of subreddits...")

    initial_count = len(subreddit_genre_sub_counts)
    logger.info(f"Initial count: {initial_count}")

    for sub, info in list(subreddit_genre_sub_counts.items()):
        genre = info["genre"]
        subscriber_count = info["subscribers"]
        if (
            (genre not in genres_whitelist)
            or (sub in subreddit_blacklist)
            or (subscriber_count < subscriber_min_count)
        ):
            del subreddit_genre_sub_counts[sub]
            # logger.info("Removing ", sub)

    final_count = len(subreddit_genre_sub_counts)
    logger.info(f"Final count: {final_count}")

    removed_count = initial_count - final_count
    logger.info(f"Removed: {removed_count}")

    return subreddit_genre_sub_counts


def get_existing_playlists(
    spotify_username,
    spotipy_client,
    playlist_base_str,
):
    # this method only gets 50 playlists at a time, so we need to cycle through to get info on all playlists
    user_playlists_object = spotipy_client.user_playlists(spotify_username, limit=50)

    all_playlists_collection = user_playlists_object["items"]
    while user_playlists_object["next"]:
        user_playlists_object = spotipy_client.next(user_playlists_object)
        all_playlists_collection += user_playlists_object["items"]

    all_playlists_collection_count = len(all_playlists_collection)
    logger.info(
        f"Found {all_playlists_collection_count} playlists for user {spotify_username}"
    )

    all_playlists_names_and_ids = [
        {"name": playlist["name"], "id": playlist["id"]}
        for playlist in all_playlists_collection
    ]

    # Delete only playlists matching the playlist_base_str format
    playlist_type_regex = re.compile(playlist_base_str.replace("{}", ".*"))
    matching_playlists = [
        {"name": x["name"], "id": x["id"]}
        for x in all_playlists_names_and_ids
        if playlist_type_regex.match(x["name"])
    ]
    matching_playlists_count = len(matching_playlists)
    logger.info(
        f"Found {matching_playlists_count} playlists that match pattern {playlist_type_regex}"
    )
    return matching_playlists


def create_playlist(
    subreddit,
    playlist_base_str,
    spotipy_client,
    spotify_username,
):
    playlist_name = playlist_base_str.format(subreddit)
    spotipy_client.user_playlist_create(
        spotify_username,
        playlist_name,
        public=True,
    )


def get_subreddit_from_playlist_name(playlist_name, playlist_base_str):
    regex_pattern = playlist_base_str.replace("{}", "(.*)")
    match = re.search(regex_pattern, playlist_name, re.IGNORECASE)
    return match.group(1)


def get_subreddits_with_existing_playlists(
    cleaned_subreddit_dic, existing_playlists, playlist_base_str
):

    subreddits_with_existing_playlists = []

    for playlist_name_and_id in existing_playlists:

        playlist_name = playlist_name_and_id["name"]
        playlist_id = playlist_name_and_id["id"]

        playlist_subreddit_name = get_subreddit_from_playlist_name(
            playlist_name, playlist_base_str
        )
        if playlist_subreddit_name in cleaned_subreddit_dic.keys():
            subreddits_with_existing_playlists.append(playlist_subreddit_name)
    #     else:
    #         logger.warning(f"{playlist_subreddit_name} NOT FOUND")
    #
    return subreddits_with_existing_playlists
