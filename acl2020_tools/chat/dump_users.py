import argparse
import json

import pandas as pd
import yaml
from requests import sessions
from rocketchat_API.rocketchat import RocketChat

offset_delta = 100


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="RocketChat user information retrieval"
    )
    parser.add_argument("--config", default="config.yml", help="Configuration yaml")
    parser.add_argument(
        "--no-email", action="store_true", help="Don't pull user emails"
    )
    parser.add_argument(
        "--no-timezone", action="store_true", help="Don't pull user timezone"
    )
    parser.add_argument(
        "--no-lastlogin", action="store_true", help="Don't pull user last login"
    )
    return parser.parse_args()


def join_emails(emails):
    if not isinstance(emails, dict):
        return ""
    delimiter = "|"
    assert all(
        [delimiter not in address for address in emails["address"]]
    ), "Character used for delimiter appears in an email address"
    return delimiter.join(emails["address"])


def get_all_users(rocket, fields_string):
    user_list = []
    offset = 0
    total = 99999999
    while offset < total:
        response = rocket.users_list(
            fields=fields_string, offset=offset, count=offset_delta
        ).json()
        total = response["total"]
        user_list.extend(response["users"])
        offset += response["count"]
        print("Loaded {}/{}".format(offset, total))
    return user_list


def get_rocketchat_fields():
    fields = dict()
    fields["name"] = 1
    fields["username"] = 1
    fields["emails"] = {"address": 1}
    fields["lastLogin"] = 1
    fields["utcOffset"] = 1
    return fields


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

        fields = get_rocketchat_fields()
        if args.no_email:
            fields["emails"]["address"] = 0
        if args.no_timezone:
            fields["utcOffset"] = 0
        if args.no_lastlogin:
            fields["lastLogin"] = 0
        fields_string = json.dumps(fields)

        users = get_all_users(rocket, fields_string)
        df = pd.DataFrame(users)

        if "email" in df:
            df["email"] = df["email"].apply(join_emails)
        if "email" not in df and not args.no_email:
            print("WARN: emails not retrieved; do you have permission?")
        if "lastLogin" not in df and not args.no_lastlogin:
            print("WARN: last login not retrieved; do you have permission?")

        df.to_csv("rocketchat-user-details.csv", index=False)


if __name__ == "__main__":
    main()
