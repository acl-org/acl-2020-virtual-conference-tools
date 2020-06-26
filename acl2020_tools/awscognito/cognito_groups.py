# pylint: disable=global-statement,redefined-outer-name
""" Script used to create|disable AWS Cognito user """
import argparse
from dataclasses import dataclass
from typing import Any, Dict

import yaml

import cognito


@dataclass(frozen=True)
class Group:
    """ Class for AWS Cognito group """

    name: str
    description: str


@dataclass(frozen=True)
class User:
    """ Class for AWS Cognito user """

    username: str
    email: str
    name: str


def load_data(aws_profile):
    """ Load the profile data """
    data: Dict[str, Any] = {}
    data["profile"] = yaml.load(open(aws_profile).read(), Loader=yaml.SafeLoader)
    data["client"] = cognito.init_client(data["profile"])

    return data


def parse_arguments():
    """ Parse Arguments """
    parser = argparse.ArgumentParser(
        description="AWS Cognito User Command Line",
        # usage="cognito_user.py [-h] [--check] [-d|-e] user_file aws_profile",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-d",
        "--disable",
        action="store",
        dest="group_to_disable",
        help="Disable users in specified group",
    )
    group.add_argument(
        "-e",
        "--enable",
        action="store",
        dest="group_to_enable",
        help="Enable users in specified group",
    )
    group.add_argument(
        "-l",
        "--list-groups",
        action="store_true",
        default=False,
        help="Disable users listed in the file",
    )
    parser.add_argument("aws_profile", help="The file contains AWS profile")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    data = load_data(args.aws_profile)

    # We can list groups, disable or enable group users now
    if args.list_groups:
        # List existing groups
        groups = cognito.list_groups(data["client"], data["profile"])
        for group in groups:
            print(f"{group.name}:\t{group.description}")
    elif args.group_to_disable:
        # Disable group users
        users = cognito.list_group_users(
            data["client"], data["profile"], args.group_to_disable
        )
        for user in users:
            cognito.disable_user(data["client"], data["profile"], user)
    elif args.group_to_enable:
        # Enable group users
        users = cognito.list_group_users(
            data["client"], data["profile"], args.group_to_enable
        )
        for user in users:
            cognito.enable_user(data["client"], data["profile"], user)
