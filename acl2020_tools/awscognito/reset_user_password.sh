#!/usr/bin/env bash

AWS_USER_POOL_ID="us-east-1_lr10OX54W"
AWS_PROFILE="virtual-acl2020"

email=$1


aws cognito-idp admin-set-user-password \
  --user-pool-id ${AWS_USER_POOL_ID} \
  --username ${email} \
  --password "7B0lbNb^sB" \
  --profile virtual-acl2020-cognito

