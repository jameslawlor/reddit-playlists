import re
from functions.base_logger import logger
import os
from praw import Reddit


def get_reddit_client():

    if os.path.exists("praw.ini"):
        cli = Reddit("bot1")
    else:
        cli = Reddit(
            client_id=os.getenv("PRAW_CLIENT_ID"),
            client_secret=os.getenv("PRAW_CLIENT_SECRET"),
            user_agent=os.getenv("PRAW_USER_AGENT"),
        )

    return cli


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

    logger.info("Getting genres and subreddits from /r/Music wiki")

    for line in trimmed_wikipage:
        if re.search(genre_regex, line):
            current_genre = line.replace("##", "")
        elif re.search(subreddit_regex, line):
            subreddit = line.split("/r/")[1].split(" ")[0]
            subreddit_genre_mappings[subreddit] = {"genre": current_genre}
        else:
            pass

    logger.info("Finished getting genres and subreddits")
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

    logger.info(f"Getting subreddit subscriber counts")

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
        logger.info(f"/r/{subreddit} processed with {subscriber_count} subscribers")

    logger.info("Subreddit subscriber counts completed")

    return subreddits_and_genres_to_output


def get_subreddit_weekly_top_posts(reddit, subreddit, n_top_posts_to_check):
    s = reddit.subreddit(subreddit)
    return list(s.top(time_filter="week", limit=n_top_posts_to_check))


def get_artists_and_tracks_from_submissions(submissions, regex_pattern):
    artists_and_tracks = []

    for submission in submissions:
        submission_title = submission.title
        artist, track = get_artist_and_track_from_submission(
            submission_title, regex_pattern
        )

        if artist and track:
            artists_and_tracks.append((artist, track))

    return artists_and_tracks


def get_artist_and_track_from_submission(submission_title, regex_pattern):
    submission_stripped = re.sub(
        r"[\(\[].*?[\)\]]", "", submission_title
    )  # remove everything in brackets
    info = re.split(regex_pattern, submission_stripped)
    if len(info) == 2:
        artist = info[0].strip()
        track = info[1].strip()
        return artist, track
    else:
        return None, None


def filter_submissions_matching_track_format(
    submissions, post_regex_pattern, allowed_domains
):

    filtered_submissions = []
    for submission in list(submissions):
        submission_url = submission.url
        submission_title = submission.title
        if does_submission_match_track_format(
            submission_url, submission_title, post_regex_pattern, allowed_domains
        ):

            filtered_submissions.append(submission)
    return filtered_submissions


def does_submission_match_track_format(
    submission_url, submission_title, regex_pattern, allowed_domains
):
    """Parse submission and decide whether we'll look it up on Spotify"""
    domain_match = any(s in submission_url for s in allowed_domains)

    # remove strings enclosed in brackets, sometimes extra info like Year of release, album, country, etc.
    stripped_submission = re.sub(r"[\(\[].*?[\)\]]", "", submission_title)
    regex_match = re.search(regex_pattern, stripped_submission)

    if (domain_match) and (regex_match):
        return True
    else:
        return False
