# pylint: disable=global-statement,redefined-outer-name
""" Script used to list AWS Cognito users """
import argparse
from dataclasses import asdict, dataclass

import pandas
import yaml

import cognito  # type: ignore


@dataclass(frozen=True)
class User:
    """ Class for AWS Cognito user """

    email: str
    name: str
    committee: str = "attendee"

    # def name(self) -> str:
    #     """ Generate the name field """
    #     return f"{self.first_name} {self.last_name}"


def load_data(aws_profile, is_debug=False):
    """ Load the profile data and get pool user """
    profile = yaml.load(open(aws_profile).read(), Loader=yaml.SafeLoader)
    client = cognito.init_client(profile)
    result = []

    users = cognito.list_users(client, profile)
    for user in users:
        if is_debug:
            print(
                f"user: {user.name()} <{user.email}>, enabled: {user.enabled}, email_verified: {user.email_verified}"
            )
        result.append(User(name=user.name(), email=user.email))

    return result


def parse_arguments():
    """ Parse Arguments """
    parser = argparse.ArgumentParser(
        description="AWS Cognito List Command Line",
        # usage="cognito_user.py [-h] aws_profile",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Show the users is enabled or not",
    )
    parser.add_argument("aws_profile", help="The file contains AWS profile")

    return parser.parse_args()


def save_file(users, file_path):
    """ Save user information to the xlsx file """
    dataframe = pandas.DataFrame([asdict(x) for x in users])
    dataframe.to_csv(file_path, index=False)
    print(f"User information is written to {file_path}")


if __name__ == "__main__":
    args = parse_arguments()
    users = load_data(args.aws_profile, args.debug)

    save_file(users, "all_users.csv")
