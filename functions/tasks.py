from functions.reddit import (
    get_subreddit_genre_mapping,
    get_subreddit_subscriber_count,
)
from functions.spotipy import (
    get_spotipy_client,
    clean_subreddits,
    get_existing_playlists,
)
from functions.filetools import load_subreddit_genre_sub_counts, write_dict_json
from praw import Reddit
import datetime
import os


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


def create_playlists(
    genres_whitelist,
    subreddit_blacklist,
    playlist_base_str,
    input_dir,
    input_file,
    output_dir,
    subscriber_min_count,
):
    reddit_instance = Reddit("bot1")
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

    # subreddits_without_existing_playlists = get_subreddits_without_existing_playlists(
    #     cleaned_subreddit_dic, existing_playlists, playlist_base_str
    # )
    # print(cleaned_subreddit_dic)
    # print(existing_playlists)
    #
    # for subreddit in subreddits_without_existing_playlists:
    #     playlist_name = playlist_base_str.format(subreddit)
    #     spotipy.user_playlist_create(spotify_username, playlist_name, public=True,)

    # for (sub, info) in cleaned_subreddit_dic.items():
    #     if
    # playlist_base_str
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
