from functions.reddit import (
    get_subreddits_and_genres,
    get_subreddit_subscriber_count,
    write_dict_to_csv,
)
import logging
from praw import Reddit
import datetime
import os

logging.getLogger().setLevel(logging.INFO)


if __name__ == "__main__":
    reddit_instance = Reddit("bot1")
    subreddits_and_genres = get_subreddits_and_genres(reddit_instance)
    subreddits_and_genres_trimmed = get_subreddit_subscriber_count(
        reddit_instance, subreddits_and_genres
    )

    filename = "subreddits-status-{date:%Y-%m-%d_%H:%M:%S}.csv".format(
        date=datetime.datetime.now()
    )
    data_folder = "data"
    output_location = os.path.join(data_folder, filename)
    write_dict_to_csv(subreddits_and_genres_trimmed, output_location)
