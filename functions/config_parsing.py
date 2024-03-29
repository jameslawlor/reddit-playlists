from functions.base_logger import logger
from argparse import ArgumentParser
import yaml


def get_config():

    parser = ArgumentParser()
    parser.add_argument("-t", "--task", dest="task", help="task", required=True)
    parser.add_argument(
        "--test",
        dest="test_mode_enabled",
        help="test",
        required=False,
        action="store_true",
    )
    args = parser.parse_args()
    task = args.task

    logger.info(f"Passed args: {args}")

    config_file = f"./configs/task_{task}.yaml"

    with open(config_file, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    logger.info(f"Running task: {task}")
    logger.info("Config: \n {}".format(yaml.dump(config)))

    return config, args
