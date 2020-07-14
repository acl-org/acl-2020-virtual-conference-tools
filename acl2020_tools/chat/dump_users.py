import argparse
import json

import pandas as pd
import yaml
from requests import sessions
from rocketchat_API.rocketchat import RocketChat
from tqdm.auto import tqdm

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

    parser.add_argument("--add-roles", action="store_true", help="Get user roles")
    return parser.parse_args()


def join_emails(emails):
    if not isinstance(emails, list):
        return ""
    mails = [m["address"] for m in emails]
    delimiter = ","
    assert all(
        [delimiter not in address for address in mails]
    ), "Character used for delimiter appears in an email address"
    return delimiter.join(mails)


def get_all_users(rocket, fields_string):
    user_list = []
    offset = 0
    total = 99999999
    while offset < total:
        response = rocket.users_list(
            fields=fields_string, offset=offset, count=offset_delta
        )
        if response.status_code != 200:
            print("There was an error")
            print(response.reason)
            break

        response = response.json()

        total = response["total"]
        user_list.extend(response["users"])
        offset += response["count"]
        print("Loaded {}/{}".format(offset, total))

    return user_list


def get_rocketchat_fields(args):
    fields = {
        "name": 1,
        "username": 1,
        "emails": 0 if args.no_email else 1,
        "utcOffset": 0 if args.no_timezone else 1,
        "no_lastlogin": 0 if args.no_lastlogin else 1,
    }

    return fields


def add_roles(users, rocket):
    print("Adding user roles")
    for user in tqdm(users):
        resp = rocket.users_info(user["_id"])

        if not resp.ok:
            print(f"Couldn't retrieve info of {user['name']} -- skipping")

        user_info = resp.json()["user"]
        user["roles"] = ",".join(user_info["roles"])


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

        fields = get_rocketchat_fields(args)

        fields_string = json.dumps(fields)

        print(fields_string)
        users = get_all_users(rocket, fields_string)

        if args.add_roles:
            add_roles(users, rocket)

        df = pd.DataFrame(users)

        if "emails" in df:
            df["email"] = df["emails"].apply(join_emails)
        if "email" not in df and not args.no_email:
            print("WARN: emails not retrieved; do you have permission?")
        if "lastLogin" not in df and not args.no_lastlogin:
            print("WARN: last login not retrieved; do you have permission?")

        df.to_csv("rocketchat-user-details.csv", index=False)


if __name__ == "__main__":
    main()
