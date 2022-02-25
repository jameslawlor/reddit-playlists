from functions.reddit import (
    get_subreddit_genre_mapping,
    get_subreddit_subscriber_count,
    get_subreddit_weekly_top_posts,
    filter_submissions_matching_track_format,
    get_artists_and_tracks_from_submissions,
)
from functions.spotipy import (
    get_spotipy_client,
    clean_subreddits,
    get_existing_playlists,
    get_subreddits_with_existing_playlists,
    get_subreddits_without_existing_playlists,
    unify_data,
    clear_playlist,
    search_spotify_for_artists_and_tracks,
    add_uris_to_playlist,
)
from functions.filetools import (
    load_subreddit_genre_sub_counts,
    write_dict_json,
    export_list_to_md,
)
from functions.base_logger import logger

from praw import Reddit
import datetime
import os
import time
import pandas as pd


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
    existing_playlists_names = [x["playlist_name"] for x in existing_playlists]
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

    subreddits_with_existing_playlists = get_subreddits_with_existing_playlists(
        unified_data_dic
    )
    subreddits_without_existing_playlists = get_subreddits_without_existing_playlists(
        unified_data_dic
    )

    if subreddits_with_existing_playlists:
        logger.info("Found subreddits_with_existing_playlists:")
        logger.info(subreddits_with_existing_playlists)

    if subreddits_without_existing_playlists:
        logger.info("Found subreddits_without_existing_playlists:")
        logger.info(subreddits_without_existing_playlists)

    logger.info(
        "Will create {} playlists".format(len(subreddits_without_existing_playlists))
    )

    for subreddit in subreddits_without_existing_playlists:
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
    # update unified_data_dic with new IDs
    for playlist in existing_playlists:
        subreddit = playlist["subreddit"]
        unified_data_dic[subreddit]["id"] = playlist["id"]
        unified_data_dic[subreddit]["playlist_name"] = playlist["playlist_name"]

    filename = filename_format.format(date=datetime.datetime.now())
    write_path = os.path.join(output_dir, filename)
    write_dict_json(unified_data_dic, write_path)


def update_playlists(
    max_playlist_length,
    input_dir,
    n_top_posts_to_check,
    post_regex_pattern,
    allowed_domains,
):

    spotipy, spotify_username = get_spotipy_client()
    reddit = Reddit("bot1")
    subreddit_data = load_subreddit_genre_sub_counts(input_dir=input_dir, input_file="")

    for subreddit, info in subreddit_data.items():
        playlist_id = info["id"]
        clear_playlist(spotipy, spotify_username, playlist_id)
        # # Get top weekly from Reddit
        subreddit_weekly_top_posts = get_subreddit_weekly_top_posts(
            reddit, subreddit, n_top_posts_to_check
        )
        submissions_matching_track_format = filter_submissions_matching_track_format(
            subreddit_weekly_top_posts, post_regex_pattern, allowed_domains
        )
        artists_and_tracks = get_artists_and_tracks_from_submissions(
            submissions_matching_track_format, post_regex_pattern
        )
        spotify_uris_to_add = search_spotify_for_artists_and_tracks(
            spotipy,
            artists_and_tracks,
            max_playlist_length,
        )
        add_uris_to_playlist(
            spotipy,
            spotify_username,
            playlist_id,
            spotify_uris_to_add,
        )

        submissions_matching_track_format_count = len(submissions_matching_track_format)
        spotify_uris_to_add_count = len(spotify_uris_to_add)
        logger.info(
            f"Processing {subreddit}: Found {submissions_matching_track_format_count} reddit submissions matching track format in top weekly {n_top_posts_to_check}, added {spotify_uris_to_add_count} to Spotify Playlist ID {playlist_id}"
        )
        time.sleep(3)  # Avoid hitting API call limit


def generate_subreddit_playlist_links_markdown_file(
    input_dir,
    input_file,
    output_dir,
    output_filename,
):
    out_txt = []
    subreddit_data = load_subreddit_genre_sub_counts(input_dir, input_file)
    df = pd.DataFrame.from_dict(subreddit_data, orient="index")
    genres = list(df["genre"].unique())
    for genre in genres:
        out_txt.append(f"## {genre}")
        subreddits_in_genre = [
            subreddit
            for subreddit in subreddit_data.keys()
            if subreddit_data[subreddit]["genre"] == genre
        ]
        for subreddit in subreddits_in_genre:
            playlist_id = subreddit_data[subreddit]["id"]
            playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
            out_txt.append(f"* [/r/{subreddit}]({playlist_url}) \n")

    write_path = os.path.join(output_dir, output_filename)
    export_list_to_md(out_txt, write_path)
