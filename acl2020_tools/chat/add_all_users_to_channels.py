import argparse

import pandas as pd
import yaml
from requests import sessions
from rocketchat_API.rocketchat import RocketChat


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="RocketChat user information retrieval"
    )
    parser.add_argument("--config", default="config.yml", help="Configuration yaml")
    parser.add_argument(
        "--channel-dump",
        default="channels.csv",
        help="Channel details dumped from rocketchat",
    )
    parser.add_argument(
        "--input",
        default="all_user_channels.txt",
        help="List of channels to add all users to (one channel per line)",
    )
    parser.add_argument("--test", action="store_true", help="Do dry run")
    return parser.parse_args()


def main():
    args = parse_arguments()
    config = yaml.load(open(args.config))

    with sessions.Session() as session:
        rocket = RocketChat(
            user_id=config["user_id"],
            auth_token=config["auth_token"],
            server_url=config["server"],
            session=session,
        )

        channel_dump = pd.read_csv(args.channel_dump)

        with open(args.input) as f:
            destination_channels = [channel.strip() for channel in f]
            destination_channels = [
                channel for channel in destination_channels if channel != ""
            ]

        nonexistent_channels = set(destination_channels) - set(channel_dump["name"])
        assert len(nonexistent_channels) == 0, "Some channels not found: " + str(
            nonexistent_channels
        )

        channel_ids = channel_dump[channel_dump["name"].isin(destination_channels)][
            "_id"
        ]

        for channel_name, channel in zip(destination_channels, channel_ids):
            if not args.test:
                rocket.channels_add_all(channel)
            print('Added all users to channel "{}"'.format(channel_name))


if __name__ == "__main__":
    main()
