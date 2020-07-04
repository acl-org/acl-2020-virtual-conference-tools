"""
Script to add roles to users

Input is a CSV like this:

user,roles
username1,"role1,role2,..."
username2,"role1,role2,..."

For example, use this to test the script:

user,roles
juan.manuel.perez,"user,volunteer"
hao.fang,"admin
"""
import argparse

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
    parser.add_argument("--role-file", help="Role CSV")
    return parser.parse_args()


def main():
    """
    Set roles to users, according to a CSV with this format:

    user,roles
    username1, "role1, role2, ..."
    """
    args = parse_arguments()
    config = yaml.load(open(args.config))
    with sessions.Session() as session:
        rocket = RocketChat(
            user_id=config["user_id"],
            auth_token=config["auth_token"],
            server_url=config["server"],
            session=session,
        )

        df = pd.read_csv(args.role_file)
        # This is awful, but I have to do it as it is not implemented in
        # RocketChat API, and also to avoid pylint's complaining

        def add_role(user, role):
            boundmethod = getattr(rocket, "_RocketChat__call_api_post")

            return boundmethod(
                method="roles.addUserToRole", roleName=role, username=user
            ).json()

        for _, row in df.iterrows():
            roles = row.roles.split(",")
            user = row.user
            for role in roles:
                resp = add_role(user, role)

                if not resp["success"]:
                    print(
                        f"Couldn't set {row.user} as {role} -- permission issue? does role exist?"
                    )


if __name__ == "__main__":
    main()
