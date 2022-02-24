from functions.reddit import (
    get_subreddit_genre_mapping,
    get_subreddit_subscriber_count,
)
from functions.spotipy import (
    get_spotipy_client,
    clean_subreddits,
    get_existing_playlists,
    get_subreddits_with_existing_playlists,
    unify_data,
)
from functions.filetools import load_subreddit_genre_sub_counts, write_dict_json
from functions.base_logger import logger

from praw import Reddit
import datetime
import os
import time


def get_subreddits_and_genres(
    genre_section_start_regex,
    genre_section_end_regex,
    genre_regex,
    subreddit_regex,
    filename_format,
    data_folder,
    test_mode,
    save_data,
):
    reddit_instance = Reddit("bot1")
    subreddits_and_genres = get_subreddit_genre_mapping(
        reddit_instance,
        genre_section_start_regex,
        genre_section_end_regex,
        genre_regex,
        subreddit_regex,
    )
    subreddits_and_genres_trimmed = get_subreddit_subscriber_count(
        reddit_instance, subreddits_and_genres, test_mode
    )

    if save_data:
        filename = filename_format.format(date=datetime.datetime.now())
        output_location = os.path.join(data_folder, filename)
        write_dict_json(subreddits_and_genres_trimmed, output_location)


def delete_playlists(
    playlist_base_str,
):
    """
    Deletes all spotify playlists for user that match input playlist string
    """

    spotipy, spotify_username = get_spotipy_client()
    existing_playlists = get_existing_playlists(
        spotify_username, spotipy, playlist_base_str
    )
    existing_playlists_ids = [x["id"] for x in existing_playlists]
    existing_playlists_names = [x["name"] for x in existing_playlists]
    for (playlist_id, playlist_name) in zip(
        existing_playlists_ids, existing_playlists_names
    ):
        logger.info(f"Deleting {playlist_name}")
        spotipy.user_playlist_unfollow(spotify_username, playlist_id)

    logger.info("Playlists deleted")


def create_empty_playlists(
    genres_whitelist,
    subreddit_blacklist,
    playlist_base_str,
    input_dir,
    input_file,
    output_dir,
    filename_format,
    subscriber_min_count,
):

    spotipy, spotify_username = get_spotipy_client()
    subreddit_genre_sub_counts = load_subreddit_genre_sub_counts(
        input_dir=input_dir, input_file=input_file
    )

    cleaned_subreddit_dic = clean_subreddits(
        subreddit_genre_sub_counts,
        genres_whitelist,
        subreddit_blacklist,
        subscriber_min_count,
    )

    existing_playlists = get_existing_playlists(
        spotify_username, spotipy, playlist_base_str
    )

    unified_data_dic = unify_data(cleaned_subreddit_dic, existing_playlists)
    print(unified_data_dic)
    stop
    subreddits_with_existing_playlists = get_subreddits_with_existing_playlists(
        cleaned_subreddit_dic, existing_playlists, playlist_base_str
    )
    logger.info("Found subreddits_with_existing_playlists:")
    logger.info(subreddits_with_existing_playlists)
    if subreddits_with_existing_playlists:
        subreddits_to_create_playlists_for = [
            subreddit
            for subreddit in list(cleaned_subreddit_dic.keys())
            if subreddit not in subreddits_with_existing_playlists
        ]
    else:
        subreddits_to_create_playlists_for = list(cleaned_subreddit_dic.keys())

    logger.info(
        "Will create {} playlists".format(len(subreddits_to_create_playlists_for))
    )
    for subreddit in subreddits_to_create_playlists_for:
        playlist_name = playlist_base_str.format(subreddit)
        spotipy.user_playlist_create(
            spotify_username,
            playlist_name,
            public=True,
        )
        time.sleep(1)  # Avoid hitting API call limit
        logger.info(f"Creating playlist for {subreddit}")

    # Get all playlist info and IDs and write to file
    existing_playlists = get_existing_playlists(
        spotify_username, spotipy, playlist_base_str
    )

    filename = filename_format.format(date=datetime.datetime.now())
    write_path = os.path.join(output_dir, filename)
    write_dict_json(existing_playlists, write_path)
