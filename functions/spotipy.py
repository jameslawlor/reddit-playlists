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
):

    logger.info("Cleaning list of subreddits...")

    initial_count = len(subreddit_genre_sub_counts)
    logger.info(f"Initial count: {initial_count}")

    for sub, info in list(subreddit_genre_sub_counts.items()):
        genre = info["genre"]
        if (genre not in genres_whitelist) or (sub in subreddit_blacklist):
            del subreddit_genre_sub_counts[sub]
            print("Remove ", sub)

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
    all_playlists_collection = spotipy_client.user_playlists(spotify_username)["items"]
    all_playlists_names = [playlist["name"] for playlist in all_playlists_collection]

    playlist_type_regex = re.compile(playlist_base_str.replace("{}", ".*"))
    existing_playlists = list(filter(playlist_type_regex.match, all_playlists_names))

    return existing_playlists


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


#
# for sub in subs:
# 	playlist_name = '/r/{} top weekly tracks'.format(sub)
# 	spotify.user_playlist_create(spotify_username, playlist_name, public=True,)
# 	# Get playlist ID
# 	playlist_ids = []
# 	for pl in [_ for _ in spotify.user_playlists(spotify_username)['items']]:
# 		if pl['name'] == playlist_name:
# 			playlist_ids.append(pl['id'])
# 	assert len(playlist_ids) == 1
# 	playlist_id = playlist_ids[0]
# 	print("sub:", sub)
# 	print("PLAYLIST ID:", playlist_id)
# 	time.sleep(1) # Avoid hitting API call limit
# 	with open('subs_completed.txt', 'a') as fp:
# 		fp.write("{}\t{}\n".format(sub, playlist_id))
