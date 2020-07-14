#
# This lambda function uses `email` and `name` from the event
# to create a user in the 'attendees' user group in Cognito
# pool in the same region
#
# Configuration:
#  ACL2020_USER_POOL_ID - environment variable specifying
#
# IAM policies for the lambda's role:
#  AWSLambdaBasicExecutionRole - required by default
#  AmazonCognitoPowerUser - yes, not that secure, but works for test
#
# Runtime:
#   Python 3.7

import json
import os
from dataclasses import dataclass

import boto3

import cognito  # type: ignore


@dataclass(frozen=True)
class User:
    """ Class for AWS Cognito user """

    email: str
    name: str
    committee: str = ""


profile = {"user_pool_id": os.environ["ACL2020_USER_POOL_ID"]}
client = boto3.client("cognito-idp")


def lambda_handler(event, _context):
    print("Received event: " + json.dumps(event, indent=2))

    email, name = event["email"], event["name"]

    user = User(email=email, name=name)

    response = cognito.create_user(client, profile, user)
    cognito.show_error_response(response)

    response = cognito.add_to_group(client, profile, user, "attendees")
    cognito.show_error_response(response)

    return "OK"
