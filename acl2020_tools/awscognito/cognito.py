# pylint: disable=global-statement,redefined-outer-name
""" Script used to create|disable AWS Cognito user """
import sys
from dataclasses import dataclass

import boto3


@dataclass(frozen=True)
class CognitoGroup:
    """ Class for AWS Cognito group """

    name: str
    description: str


@dataclass(frozen=True)
class CognitoUser:
    """ Class for AWS Cognito user """

    username: str
    email: str
    custom_name: str = ""
    enabled: bool = True

    def name(self) -> str:
        """ Generate the name field """
        return self.custom_name or self.email


def __convert_aws_user__(aws_user):
    email: str = ""
    custom_name: str = ""
    enabled = aws_user["Enabled"]
    username = aws_user["Username"]
    for attr in aws_user["Attributes"]:
        if attr["Name"] == "email":
            email = attr["Value"]
        elif attr["Name"] == "custom:name":
            custom_name = attr["Value"]

    user = CognitoUser(
        username=username, email=email, custom_name=custom_name, enabled=enabled,
    )
    return user


def add_to_group(client, profile, user, group_name):
    """ Adds the specified user to the specified group """
    try:
        response = client.admin_add_user_to_group(
            UserPoolId=profile["user_pool_id"],
            Username=user.email,
            GroupName=group_name,
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(f"User {user.email} added to group {group_name}")
        return response
    except client.exceptions.UserNotFoundException as error:
        print(f"User {user.email} does not exist")
        return error.response
    except client.exceptions.ResourceNotFoundException as error:
        print(f"Group {group_name} does not exist")
        return error.response
    except client.exceptions.ClientError as error:
        print(f"Fail to add user {user.email} to group {group_name}")
        return error.response


def create_user(client, profile, user):
    """ Creates a new user in the specified user pool """
    try:
        if callable(user.name):
            name = user.name()
        else:
            name = user.name
        response = client.admin_create_user(
            UserPoolId=profile["user_pool_id"],
            Username=user.email,
            UserAttributes=[
                {"Name": "email", "Value": user.email},
                {"Name": "email_verified", "Value": "true"},
                {"Name": "custom:name", "Value": name},
            ],
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(f"User {user.email} was created successfully")
        return response
    except client.exceptions.UsernameExistsException as error:
        print(f"User {user.email} exists")
        return error.response
    except client.exceptions.ClientError as error:
        print(f"Fail to create user {user.email}")
        return error.response


def delete_user(client, profile, user):
    """ Deletes a user from the pool """
    try:
        response = client.admin_delete_user(
            UserPoolId=profile["user_pool_id"], Username=user.email
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(f"User {user.email} was deleted successfully")
        return response
    except client.exceptions.UserNotFoundException as error:
        print(f"User {user.email} does not exist")
        return error.response
    except client.exceptions.ClientError as error:
        print(f"Fail to delete user {user.email}")
        return error.response


def disable_user(client, profile, user):
    """ Disables the specified user """
    try:
        response = client.admin_disable_user(
            UserPoolId=profile["user_pool_id"], Username=user.email
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(f"User {user.email} was disabled successfully")
        return response
    except client.exceptions.UserNotFoundException as error:
        print(f"User {user.email} does not exist")
        return error.response
    except client.exceptions.ClientError as error:
        print(f"Fail to disable user {user.email}")
        return error.response


def enable_user(client, profile, user):
    """ Enables the specified user """
    try:
        response = client.admin_enable_user(
            UserPoolId=profile["user_pool_id"], Username=user.email
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(f"User {user.email} was enabled successfully")
        return response
    except client.exceptions.UserNotFoundException as error:
        print(f"User {user.email} does not exist")
        return error.response
    except client.exceptions.ClientError as error:
        print(f"Fail to disable user {user.email}")
        return error.response


def init_client(profile):
    client = boto3.client(
        "cognito-idp",
        aws_access_key_id=profile["access_key_id"],
        aws_secret_access_key=profile["secret_access_key"],
        region_name=profile["region_name"],
    )
    return client


def list_group_users(client, profile, group_name):
    result = []
    try:
        response = client.list_users_in_group(
            UserPoolId=profile["user_pool_id"], GroupName=group_name
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            aws_users = response["Users"]
            for aws_user in aws_users:
                result.append(__convert_aws_user__(aws_user))
    except client.exceptions.ResourceNotFoundException as error:
        print(f"Group {group_name} does not exist")
        sys.exit(2)
    except client.exceptions.ClientError as error:
        print(error)
        print("Fail to list groups")
        sys.exit(2)

    return result


def list_groups(client, profile):
    """ List existing groups from the pool """
    result = []
    try:
        response = client.list_groups(UserPoolId=profile["user_pool_id"])
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            groups = response["Groups"]
            for group in groups:
                result.append(
                    CognitoGroup(
                        name=group["GroupName"], description=group["Description"]
                    )
                )
    except client.exceptions.ClientError as error:
        print("Fail to list groups")
        print(error.response)
        sys.exit(2)

    return result


def list_users(client, profile):
    """ Lists all user from the pool """
    result = []
    try:
        response = client.list_users(
            UserPoolId=profile["user_pool_id"],
            # AttributesToGet=['email']
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            aws_users = response["Users"]
            for aws_user in aws_users:
                result.append(__convert_aws_user__(aws_user))

    except client.exceptions.ClientError as error:
        print("Fail to list users")
        print(error)
        sys.exit(2)

    return result
