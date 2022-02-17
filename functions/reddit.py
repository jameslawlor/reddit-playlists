import re
import logging
import pandas as pd

logging.getLogger().setLevel(logging.INFO)


def get_wikipage() -> list:
    wikipage = (
        reddit_instance.subreddit("Music")
        .wiki["musicsubreddits"]
        .content_md.splitlines()
    )
    return wikipage


def trim_wikipage(wikipage) -> list:

    genre_regex = "##.*"
    subreddit_regex = ".*/r/.*"

    genre_section_start_regex = "#Subreddits by genre.*"
    genre_section_end_regex = "#Multi-genre & community subreddits.*"

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


def get_subreddits_and_genres(reddit_instance) -> dict:
    """
    Parses list of genre subreddits from /r/Music wiki https://www.reddit.com/r/Music/wiki/musicsubreddits/
    """

    wikipage = get_wikipage()
    trimmed_wikipage = trim_wikipage()

    subreddit_genre_mappings = {}

    logging.info("Getting genres and subreddits from /r/Music wiki")

    for line in wikipage_trimmed:
        if re.search(genre_regex, line):
            current_genre = line.replace("##", "")
        elif re.search(subreddit_regex, line):
            subreddit = line.split("/r/")[1].split(" ")[0]
            subreddit_genre_mappings[subreddit] = {"genre": current_genre}
        else:
            pass

    logging.info("Finished getting genres and subreddits")

    return subreddit_genre_mappings


def get_subreddit_subscriber_count(
    reddit_instance: object, subreddits_and_genres: dict, subscriber_min_count=10000
) -> dict:

    logging.info(
        f"Getting subreddit subscriber counts and dropping subreddits under threshold {subscriber_min_count}"
    )

    subreddits_and_genres_to_output = {}

    for (subreddit, values) in list(subreddits_and_genres.items())[:5]:
        subscriber_count = reddit_instance.subreddit(subreddit).subscribers
        genre = values["genre"]
        if subscriber_count >= subscriber_min_count:
            subreddits_and_genres_to_output[subreddit] = {
                "genre": genre,
                "subscribers": subscriber_count,
            }
            logging.info(
                f"/r/{subreddit} processed with {subscriber_count} subscribers"
            )
        else:
            logging.info(
                f"/r/{subreddit} dropped due to too few subscribers, {subscriber_count} found but needed > {subscriber_min_count}"
            )

    logging.info("Subreddit subscriber counts completed")

    return subreddits_and_genres_to_output


def write_dict_to_csv(dict, write_path):
    logging.info(f"Writing to {write_path}")
    logging.info(dict)
    df = pd.DataFrame.from_dict(dict).T
    df.index.name = "subreddit"
    logging.info(f"output df head\n {df.head()}")
    df.to_csv(write_path)


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
    output_location = os.path.join("..", data_folder, filename)
    write_dict_to_csv(subreddits_and_genres_trimmed, output_location)
