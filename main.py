from functions.config_parsing import get_config
from functions.tasks import (
    get_subreddits_and_genres,
    create_empty_playlists,
    delete_playlists,
    update_playlists,
    generate_subreddit_playlist_links_markdown_file,
)
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
            save_data=config["save_data"],
            filename_format=config["filename_format"],
            data_folder=config["data_folder"],
            test_mode=config["test_mode"],
        )
    elif task == "create_empty_playlists":
        create_empty_playlists(
            genres_whitelist=config["genres_whitelist"],
            subreddit_blacklist=config["subreddit_blacklist"],
            playlist_base_str=config["playlist_base_str"],
            input_dir=config["input_dir"],
            input_file=config["input_file"],
            output_dir=config["output_dir"],
            subscriber_min_count=config["subscriber_min_count"],
            filename_format=config["filename_format"],
        )
    elif task == "delete_playlists":
        delete_playlists(
            playlist_base_str=config["playlist_base_str"],
        )
    elif task == "update_playlists":
        update_playlists(
            max_playlist_length=config["max_playlist_length"],
            input_dir=config["input_dir"],
            n_top_posts_to_check=config["n_top_posts_to_check"],
            post_regex_pattern=config["post_regex_pattern"],
            allowed_domains=config["allowed_domains"],
        )
    elif task == "generate_subreddit_playlist_links_markdown_file":
        generate_subreddit_playlist_links_markdown_file(
            input_dir=config["input_dir"],
            input_file=config["input_file"],
            output_dir=config["output_dir"],
            output_filename=config["output_filename"],
        )
    else:
        raise ValueError("Task not recognised!")
