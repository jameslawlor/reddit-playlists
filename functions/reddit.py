import re
import logging

logging.getLogger().setLevel(logging.INFO)


def get_wikipage(reddit_instance) -> list:
    wikipage = (
        reddit_instance.subreddit("Music")
        .wiki["musicsubreddits"]
        .content_md.splitlines()
    )
    return wikipage


def trim_wikipage(
    wikipage: list, genre_section_start_regex: str, genre_section_end_regex: str
) -> list:

    genre_section_start_ix = [
        ix
        for ix, line in enumerate(wikipage)
        if re.search(genre_section_start_regex, line)
    ][0]

    genre_section_end_ix = [
        ix
        for ix, line in enumerate(wikipage)
        if re.search(genre_section_end_regex, line)
    ][0]

    return wikipage[genre_section_start_ix + 1 : genre_section_end_ix]


def parse_wikipage(trimmed_wikipage, genre_regex, subreddit_regex):
    subreddit_genre_mappings = {}

    logging.info("Getting genres and subreddits from /r/Music wiki")

    for line in trimmed_wikipage:
        if re.search(genre_regex, line):
            current_genre = line.replace("##", "")
        elif re.search(subreddit_regex, line):
            subreddit = line.split("/r/")[1].split(" ")[0]
            subreddit_genre_mappings[subreddit] = {"genre": current_genre}
        else:
            pass

    logging.info("Finished getting genres and subreddits")
    return subreddit_genre_mappings


def get_subreddit_genre_mapping(
    reddit_instance,
    genre_section_start_regex,
    genre_section_end_regex,
    genre_regex,
    subreddit_regex,
) -> dict:
    """
    Parses list of genre subreddits from /r/Music wiki https://www.reddit.com/r/Music/wiki/musicsubreddits/
    """

    wikipage = get_wikipage(reddit_instance)
    trimmed_wikipage = trim_wikipage(
        wikipage, genre_section_start_regex, genre_section_end_regex
    )
    subreddit_genre_mappings = parse_wikipage(
        trimmed_wikipage, genre_regex, subreddit_regex
    )
    return subreddit_genre_mappings


def get_subreddit_subscriber_count(
    reddit_instance,
    subreddits_and_genres: dict,
    test_mode: bool,
) -> dict:

    logging.info(f"Getting subreddit subscriber counts")

    subreddits_and_genres_to_output = {}

    if test_mode:
        list_of_subreddits_and_genres = list(subreddits_and_genres.items())[:10]
    else:
        list_of_subreddits_and_genres = list(subreddits_and_genres.items())

    for (subreddit, values) in list_of_subreddits_and_genres:
        try:
            subscriber_count = reddit_instance.subreddit(subreddit).subscribers
        except:
            # Catch 404s when subreddit banned or doesnt exist
            subscriber_count = -1

        genre = values["genre"]

        subreddits_and_genres_to_output[subreddit] = {
            "genre": genre,
            "subscribers": subscriber_count,
        }
        logging.info(f"/r/{subreddit} processed with {subscriber_count} subscribers")

    logging.info("Subreddit subscriber counts completed")

    return subreddits_and_genres_to_output
