from functions.config_parsing import get_config
from functions.tasks import get_subreddits_and_genres
import logging

logging.getLogger().setLevel(logging.INFO)


if __name__ == "__main__":

    config = get_config()
    task = config["task"]

    if task == "get_subreddits_and_genres":
        get_subreddits_and_genres(
            genre_section_start_regex=config["genre_section_start_regex"],
            genre_section_end_regex=config["genre_section_end_regex"],
            genre_regex=config["genre_regex"],
            subreddit_regex=config["subreddit_regex"],
            subscriber_min_count=config["subscriber_min_count"],
            save_data=config["save_data"],
            filename_format=config["filename_format"],
            data_folder=config["data_folder"],
            test_mode=config["test_mode"],
        )
    else:
        raise ValueError("Task not recognised!")
