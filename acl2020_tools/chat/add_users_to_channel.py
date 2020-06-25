import argparse
import sys

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
        "--user-dump",
        default="rocketchat-user-details.csv",
        help="User details dumped from rocketchat",
    )
    parser.add_argument(
        "--channel-dump",
        default="channels.csv",
        help="Channel details dumped from rocketchat",
    )
    parser.add_argument(
        "--input",
        default="user-to-channels.csv",
        help="List of users and channels to add them to (CSV or Excel)",
    )
    parser.add_argument("--test", action="store_true", help="Do dry run")
    return parser.parse_args()


def load_pandas(path):
    if path.endswith(".csv"):
        return pd.read_csv(path)
    elif path.endswith(".xls") or path.endswith(".xlsx"):
        return pd.read_excel(path)
    else:
        print(
            'ERROR: Path does not have recognised file format (csv|xlsx?): "{}"'.format(
                path
            )
        )
        sys.exit(1)


def find_user_id(email, user_dump):
    found_id = user_dump[user_dump.emails.apply(lambda x: email in x)]["_id"]
    assert len(found_id) != 0, 'No user found registered with email "{}"'.format(email)
    assert (
        len(found_id) == 1
    ), '>1 user found registered with email "{}" (this should not happen)'.format(email)
    return found_id.values[0]


def add_user_to_channel(user_data, rocket, test):
    user_id = user_data["user_id"]
    email = user_data["email"]
    channel = user_data["channel_name"]
    channel_id = user_data["channel_id"]
    if not test:
        rocket.channels_invite(roomId=channel_id, userId=user_id)
    print("Added user {} to channel {}".format(email, channel))


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

        user_dump = load_pandas(args.user_dump)
        channel_dump = load_pandas(args.channel_dump)
        channel_dump.rename(
            columns={"_id": "channel_id", "name": "channel_name"}, inplace=True
        )
        user_to_channel = load_pandas(args.input)

        assert "emails" in user_dump, "User dump file doesn't have an email column"
        user_dump["emails"] = user_dump["emails"].apply(
            lambda x: x.split("|") if isinstance(x, str) else ""
        )

        desired_channels = set(user_to_channel["channel"])
        existing_channels = set(channel_dump["channel_name"])
        nonexistent_channels = desired_channels - existing_channels
        assert len(nonexistent_channels) == 0, (
            "Some channels you're trying to add users to don't exist: "
            + str(nonexistent_channels)
        )

        users_with_channel_ids = user_to_channel.merge(
            channel_dump, left_on="channel", right_on="channel_name"
        )
        #  We can't just join the two df on emails because it's possible for a user to have >1 email
        users_with_channel_ids["user_id"] = users_with_channel_ids["email"].apply(
            lambda x: find_user_id(x, user_dump)
        )

        users_with_channel_ids.apply(
            lambda x: add_user_to_channel(x, rocket, args.test), axis=1
        )


if __name__ == "__main__":
    main()
