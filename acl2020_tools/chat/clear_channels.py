import argparse
import pprint
import sys
import traceback

import pandas as pd
import yaml
from requests import sessions
from rocketchat_API.rocketchat import RocketChat
from tqdm import tqdm


def parse_arguments():
    parser = argparse.ArgumentParser(description="MiniConf Portal Command Line")
    parser.add_argument(
        "--config",
        "-c",
        default="./config.yml",
        help="Configuration yaml filepath. Default: ./config.yml",
    )
    parser.add_argument(
        "--channels_file",
        "--channels",
        "-i",
        default="./channels.csv",
        help="Input channels csv or excel filepath. Must contain a _id column. "
        "Default: ./channels.csv",
    )
    return parser.parse_args()


def read_channels(channels_filepath: str) -> pd.DataFrame:
    try:
        if channels_filepath.endswith(".csv"):
            channels = pd.read_csv(channels_filepath)
        if channels_filepath.endswith(".xlsx") or channels_filepath.endswith(".xls"):
            channels = pd.read_excel(channels_filepath)
        return channels[["_id"]]
    except:
        traceback.print_exc()
        print(
            "Make sure to indicate the channels csv or excel filepath "
            "and that they contain an '_id' column"
        )
        sys.exit(1)


if __name__ == "__main__":
    args = parse_arguments()
    config = yaml.load(open(args.config), Loader=yaml.SafeLoader)

    with sessions.Session() as session:
        rocket = RocketChat(
            user_id=config["user_id"],
            auth_token=config["auth_token"],
            server_url=config["server"],
            session=session,
        )
        channels_df = read_channels(args.channels_file)
        filename = args.channels_file.split("/")[-1]
        print(
            f"Found {len(channels_df)} channel(s) in {filename}. "
            "Proceed to clear messages? [y/n]"
        )
        confirmation = input().strip().lower()
        if confirmation == "y":
            print("Clearing messages...")

            error_channels = []
            # Can make dates configurable if necessary
            oldest, latest = "2020-01-01", "2020-12-31"
            for channel_id in tqdm(channels_df["_id"]):
                response = rocket.rooms_clean_history(
                    room_id=channel_id, latest=latest, oldest=oldest
                ).json()
                if not response["success"]:
                    if response["errorType"] == "error-not-allowed":
                        print("You don't have permissions to perform this action")
                        sys.exit(1)
                    error_channels.append(channel_id)

            print(
                f"Cleared history of {len(channels_df) - len(error_channels)} channel(s)"
            )
            if error_channels:
                print(
                    "There was an error clearing the history of the "
                    "following channels: ",
                    error_channels,
                )
