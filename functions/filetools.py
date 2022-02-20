import os
import logging
import glob
import json

logging.getLogger().setLevel(logging.INFO)


def write_dict_json(dict, write_path):
    logging.info(f"Writing to {write_path}")
    logging.info(dict)
    with open(write_path, "w") as fp:
        json.dump(dict, fp)


def find_most_recent_file(dir):
    list_of_files = glob.glob1(dir, "*json")
    return max(list_of_files)


def load_subreddit_genre_sub_counts(
    input_dir,
    input_file,
):

    if not input_file:
        logging.info(
            f"Input file not specified, loading most recent file by name (creation timestamp)"
        )
        newest_file = find_most_recent_file(input_dir)
        full_path = os.path.join(input_dir, newest_file)
    else:
        full_path = os.path.join(input_dir, input_file)

    logging.info(f"Loading from {full_path}")
    with open(full_path, "r") as f:
        subreddit_dic = json.load(f)

    logging.info(subreddit_dic)
    return subreddit_dic
