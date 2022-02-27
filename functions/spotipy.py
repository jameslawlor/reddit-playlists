import configparser
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from functions.base_logger import logger
import re
import os


def get_spotipy_client():

    if os.path.exists("spotipy.cfg"):
        config = configparser.ConfigParser()
        config.read("spotipy.cfg")
        client_id = config.get("SPOTIFY", "CLIENT_ID")
        client_secret = config.get("SPOTIFY", "CLIENT_SECRET")
        username = config.get("SPOTIFY", "USERNAME")
    else:
        client_id = os.getenv("spotipy_client_id")
        client_secret = os.getenv("spotipy_client_secret")
        username = os.getenv("spotipy_client_username")

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
        open_browser=False,
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
        {"playlist_name": playlist["name"], "id": playlist["id"]}
        for playlist in all_playlists_collection
    ]

    # Filter playlists that match the playlist_base_str pattern
    playlist_type_regex = re.compile(playlist_base_str.replace("{}", ".*"))
    matching_playlists = [
        {
            "playlist_name": x["playlist_name"],
            "id": x["id"],
            "subreddit": get_subreddit_from_playlist_name(
                x["playlist_name"], playlist_base_str
            ),
        }
        for x in all_playlists_names_and_ids
        if playlist_type_regex.match(x["playlist_name"])
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


def get_subreddits_without_existing_playlists(unified_data_dic):
    subreddits_without_existing_playlists = []
    for subreddit, info in unified_data_dic.items():
        if "id" not in info.keys():
            subreddits_without_existing_playlists.append(subreddit)

    return subreddits_without_existing_playlists


def get_subreddits_with_existing_playlists(unified_data_dic):
    subreddits_with_existing_playlists = []
    for subreddit, info in unified_data_dic.items():
        if "id" in info.keys():
            subreddits_with_existing_playlists.append(subreddit)

    return subreddits_with_existing_playlists


def unify_data(cleaned_subreddit_dic, existing_playlists):

    for subreddit, info in list(cleaned_subreddit_dic.items()):
        playlist_info = [
            playlist
            for playlist in existing_playlists
            if playlist["subreddit"] == subreddit
        ]
        if len(playlist_info) == 1:
            cleaned_subreddit_dic[subreddit] = dict(info, **playlist_info[0])

    return cleaned_subreddit_dic


def clear_playlist(spotipy, spotify_username, playlist_id):
    """Clears spotify playlist at playlist_id"""
    playlist_track_list = spotipy.user_playlist_tracks(spotify_username, playlist_id)
    track_uris_to_remove = [
        track["track"]["uri"] for track in playlist_track_list["items"]
    ]
    spotipy.user_playlist_remove_all_occurrences_of_tracks(
        spotify_username, playlist_id, track_uris_to_remove
    )
    return


def spotify_search(spotify, artist, track):
    query = "artist:" + artist + " track:" + track
    return spotify.search(query, type="track")["tracks"]


def search_spotify_for_artists_and_tracks(
    spotipy, submissions_matching_track_format, max_playlist_length
):

    uris_list = []
    for (artist, track) in submissions_matching_track_format:
        search_results = spotify_search(spotipy, artist, track)
        n_matches = search_results["total"]
        if n_matches > 0:
            selected_uri = search_results["items"][0]["uri"]  # take first search result
            if selected_uri not in uris_list:
                uris_list.append(selected_uri)

        if len(uris_list) >= max_playlist_length:
            return uris_list

    return uris_list


def add_uris_to_playlist(spotify, spotify_username, playlist_id, spotify_uris_to_add):
    if len(spotify_uris_to_add) > 0:
        spotify.user_playlist_add_tracks(
            spotify_username, playlist_id=playlist_id, tracks=spotify_uris_to_add
        )
    else:
        logger.warning(
            "WARNING: No valid Spotify URIs found for this subreddit's posts"
        )
