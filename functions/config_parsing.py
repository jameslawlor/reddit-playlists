from functions.base_logger import logger
from argparse import ArgumentParser
import yaml


def get_config():

    parser = ArgumentParser()
    parser.add_argument("-t", "--task", dest="task", help="task", required=True)
    args = parser.parse_args()
    task = args.task

    if task == "get_subreddits_and_genres":
        config_file = "./configs/task_get_subreddits_and_genres.yaml"
    elif task == "create_playlists":
        config_file = "./configs/task_create_playlists.yaml"
    else:
        raise ValueError("Task not supported")

    with open(config_file, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    logger.info(f"Running task: {task}")
    logger.info("Config: \n {}".format(yaml.dump(config)))

    return config
